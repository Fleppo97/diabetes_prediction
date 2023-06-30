import os
import pkg_resources
import pyspark
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import webbrowser
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import col,isnan,when,count,explode,array,lit
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression, GBTClassifier
from pyspark.ml.feature import VectorAssembler, MinMaxScaler, StringIndexer, OneHotEncoder
from pyspark2pmml import PMMLBuilder
from openscoring import Openscoring
from sklearn import metrics
import traceback

############################################
# Inizializing Spark context and Dataframe #
############################################
# Creating spark session and context

spark = SparkSession.builder \
    .appName('DiabetesPrediction') \
    .config('spark.cassandra.connection.host', 'localhost') \
    .config('spark.cassandra.auth.username', 'cassandra') \
    .config('spark.cassandra.auth.password', 'cassandra') \
    .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.11:2.5.1")\
    .getOrCreate()



    

 
sc = spark.sparkContext

try:

    #df_unbalanced = spark.read.format('org.apache.spark.sql.cassandra').option('table', 'features').option('keyspace', 'diabetes_dataset').load()

    
# Caricamento dei dati da Cassandra
    print("0#"*200)
    print("CARICO CASSANDRA")
    
    df_unbalanced = spark.read.format("org.apache.spark.sql.cassandra") \
    .option("table", "features") \
    .option("keyspace", "diabetes_dataset") \
    .option("partitioner", "org.apache.spark.sql.cassandra.DefaultSource") \
    .option("spark.cassandra.auth.username", "cassandra") \
    .option("spark.cassandra.auth.password", "cassandra") \
    .load()          #non funziona con spark 3.3 quindi lo cancello e installo 3.2.2

    df_unbalanced = df_unbalanced.drop("id").drop('nodocbccost')
    

    ############################################
    ###### Anlizing dataset with charts ########
    ############################################
    
    # Setting Seaborn features
    sns.set_style("whitegrid")
    sns.set_palette("colorblind")
    sns.set_context("notebook", font_scale=1.5)
    
    
    #Preprocessing age

    df_temp = df_unbalanced.withColumn('age_mapped',
                                   when(col('age') == '1', '20')
                                   .when(col('age') == '2', '25')
                                   .when(col('age') == '3', '30')
                                   .when(col('age') == '4', '35')
                                   .when(col('age') == '5', '40')
                                   .when(col('age') == '6', '45')
                                   .when(col('age') == '7', '50')
                                   .when(col('age') == '8', '55')
                                   .when(col('age') == '9', '60')
                                   .when(col('age') == '10', '65')
                                   .when(col('age') == '11', '70')
                                   .when(col('age') == '12', '75')
                                   .when(col('age') == '13', '80')
                                   .otherwise(col('age')).cast('integer'))

    df_temp = df_temp.drop('age').withColumnRenamed('age_mapped', 'age')
    

    df_pd = df_temp.toPandas()
   
   
    # Selecting features 
    features = ["diabetes_binary", "highbp", "highchol", "cholcheck", "bmi", "smoker", "stroke", "heartdiseaseorattack", "physactivity", "fruits", "veggies", "hvyalcoholconsump", "anyhealthcare", "genhlth", "menthlth", "physhlth", "diffwalk", "sex", "age", "education", "income"]
    
    yes_no_feat = ["fruits","veggies","diffwalk","anyhealthcare","cholcheck","heartdiseaseorattack","highbp", "highchol","hvyalcoholconsump","physactivity","sex","smoker", "stroke", "diabetes_binary"]
	
    num_feat = [feat for feat in features if feat not in yes_no_feat]
    
    
    # map to number
    decodeVeggiesMap = {'Daily Consumption': '1', 'Non-Daily Consumption': '0'}#
    decodeSexMap = {'Male': '1', 'Female': '0'}#
    decodeFruitMap = {'Daily Consumption': '1', 'Non-Daily Consumption': '0'}
    decodeHighBP = {'High BP': '1', 'Non High BP': '0'}
    decodeHighChol = {'High Chol': '1', 'Non High Chol': '0'}#
    decodeCholCheck = {'Check in last 5y': '1', 'No Check in last 5y': '0'}
    decodeSmoker = {'Smoked 100 cigarets or more': '1', 'Smoked less than 100 cigarets': '0'}#
    decodeStroke = {'Ever had a Stroke': '1', 'Never had a Stroke': '0'}#
    decodeHearth = {'Hearth Disease or MI': '1', 'No Hearth Disease or MI': '0'}#
    decodePhysAct = {'Physically Active': '1', 'Not physically Active': '0'}#
    decodeHeavyAlcohol = {'More than 10 drinks/week': '1', 'Less than 10 drinks/week': '0'}#
    decodeAnyHealthCare = {'Any Health-care Coverage': '1', 'None Health-care Coverage': '0'}
    decodeDiffWalk = {'Difficult to Walk': '1', 'No Difficult to walk': '0'}#
    decodeDiabete = {'Diabete': '1', 'No Diabete': '0'}
    
    #Create map to words
    inverseDecodeVeggiesMap = {'1.0': 'Daily Consumption', '0.0': 'Non-Daily Consumption'}
    inverseDecodeSexMap = {'1.0': 'Male', '0.0': 'Female'}
    inverseDecodeFruitMap = {'1.0': 'Daily Consumption', '0.0': 'Non-Daily Consumption'}
    inverseDecodeHighBP = {'1.0': 'High BP', '0.0': 'Non High BP'}
    inverseDecodeHighChol = {'1.0': 'High Chol', '0.0': 'Non High Chol'}
    inverseDecodeCholCheck = {'1.0': 'Check in last 5y', '0.0': 'No Check in last 5y'}
    inverseDecodeSmoker = {'1.0': 'Smoked 100 cigarets or more', '0.0': 'Smoked less than 100 cigarets'}
    inverseDecodeStroke = {'1.0': 'Ever had a Stroke', '0.0': 'Never had a Stroke'}
    inverseDecodeHearth = {'1.0': 'Hearth Disease or MI', '0.0': 'No Hearth Disease or MI'}
    inverseDecodePhysAct = {'1.0': 'Physically Active', '0.0': 'Not physically Active'}
    inverseDecodeHeavyAlcohol = {'1.0': 'More than 10 drinks/week', '0.0': 'Less than 10 drinks/week'}
    inverseDecodeAnyHealthCare = {'1.0': 'Any Health-care Coverage', '0.0': 'None Health-care Coverage'}
    inverseDecodeDiffWalk = {'1.0': 'Difficult to Walk', '0.0': 'No Difficult to walk'}
    inverseDecodeDiabete = {'1.0': 'Diabete', '0.0': 'No Diabete'}
    
    
    # applico ---->
    df_pd['veggies'] = df_pd['veggies'].astype(str).replace(inverseDecodeVeggiesMap)
    df_pd['sex'] = df_pd['sex'].astype(str).replace(inverseDecodeSexMap)
    df_pd['fruits'] = df_pd['fruits'].astype(str).replace(inverseDecodeFruitMap)
    df_pd['highbp'] = df_pd['highbp'].astype(str).replace(inverseDecodeHighBP)
    df_pd['highchol'] = df_pd['highchol'].astype(str).replace(inverseDecodeHighChol)
    df_pd['cholcheck'] = df_pd['cholcheck'].astype(str).replace(inverseDecodeCholCheck)
    df_pd['smoker'] = df_pd['smoker'].astype(str).replace(inverseDecodeSmoker)
    df_pd['stroke'] = df_pd['stroke'].astype(str).replace(inverseDecodeStroke)
    df_pd['heartdiseaseorattack'] = df_pd['heartdiseaseorattack'].astype(str).replace(inverseDecodeHearth)
    df_pd['physactivity'] = df_pd['physactivity'].astype(str).replace(inverseDecodePhysAct)
    df_pd['hvyalcoholconsump'] = df_pd['hvyalcoholconsump'].astype(str).replace(inverseDecodeHeavyAlcohol)
    df_pd['anyhealthcare'] = df_pd['anyhealthcare'].astype(str).replace(inverseDecodeAnyHealthCare)
    df_pd['diffwalk'] = df_pd['diffwalk'].astype(str).replace(inverseDecodeDiffWalk)
    df_pd['diabetes_binary'] = df_pd['diabetes_binary'].astype(str).replace(inverseDecodeDiabete)
    
    
    #Creo i Grafici
    	
    def plotDistributionCategoricalChart(name_feature):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))  # Creazione di due assi separati

        labels = df_pd[name_feature].unique()

    # Filtrare il DataFrame per il valore di diabetes_binary == 1
        df_1 = df_pd[df_pd['diabetes_binary'] == "Diabete"]
        counts_1 = df_1[name_feature].value_counts()
        ax1.bar(counts_1.index, counts_1.values, color="red")
        #ax1.set_title("Distribution of {} for Diabetics".format(name_feature))
        ax1.set_xlabel("Diabetic")
        ax1.set_ylabel("Count")
        ax1.set_xticklabels(counts_1.index, rotation=15)

    # Filtrare il DataFrame per il valore di diabetes_binary == 0
        df_0 = df_pd[df_pd['diabetes_binary'] == "No Diabete"]
        counts_0 = df_0[name_feature].value_counts()
        ax2.bar(counts_0.index, counts_0.values, color="green")
        #ax2.set_title("Distribution of {} for Non-Diabetics".format(name_feature))
        ax2.set_xlabel("No Diabetic")
        ax2.set_ylabel("Count")
        ax2.set_xticklabels(counts_0.index, rotation=15)
        plt.tight_layout()
        plt.savefig('output/{}.png'.format(name_feature), transparent=True, facecolor='white')
        plt.close()
    for feat in yes_no_feat:
        if(feat!="diabetes_binary"):
    	    plotDistributionCategoricalChart(feat)
    
    #Creo grafico a torta per diabetes_binary
    def plotDiabetesBinaryDistribution():
        fig, ax = plt.subplots(figsize=(6, 6))

    # Calcola i conteggi per ogni valore della variabile diabetes_binary
        counts = df_pd['diabetes_binary'].value_counts()

    # Crea il grafico a torta
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_title("Distribution of diabetic patient")

        plt.tight_layout()
        plt.savefig('output/diabetes_binary.png', transparent=True, facecolor="white")
        plt.close()	
    plotDiabetesBinaryDistribution()
    
    
    # applico <----
    df_pd['veggies'] = df_pd['veggies'].replace(decodeVeggiesMap)
    df_pd['sex'] = df_pd['sex'].replace(decodeSexMap)
    df_pd['fruits'] = df_pd['fruits'].replace(decodeFruitMap)
    df_pd['highbp'] = df_pd['highbp'].replace(decodeHighBP)
    df_pd['highchol'] = df_pd['highchol'].replace(decodeHighChol)
    df_pd['cholcheck'] = df_pd['cholcheck'].replace(decodeCholCheck)
    df_pd['smoker'] = df_pd['smoker'].replace(decodeSmoker)
    df_pd['stroke'] = df_pd['stroke'].replace(decodeStroke)
    df_pd['heartdiseaseorattack'] = df_pd['heartdiseaseorattack'].replace(decodeHearth)
    df_pd['physactivity'] = df_pd['physactivity'].replace(decodePhysAct)
    df_pd['hvyalcoholconsump'] = df_pd['hvyalcoholconsump'].replace(decodeHeavyAlcohol)
    df_pd['anyhealthcare'] = df_pd['anyhealthcare'].replace(decodeAnyHealthCare)
    df_pd['diffwalk'] = df_pd['diffwalk'].replace(decodeDiffWalk)
    df_pd['diabetes_binary'] = df_pd['diabetes_binary'].replace(decodeDiabete)  
    #converto le colonne in float
    for column in df_pd.columns:
        df_pd[column] = df_pd[column].astype(float)
    
    
    
    # Grafici di distribuzione
    def plotContinuousChart(name_feature):
    	plt.rcParams.update({'font.size': 14})  # Aumenta la dimensione dei caratteri
    	fig, ax = plt.subplots(figsize=(25, 9))
    	sns.set_style("whitegrid")
    	sns.kdeplot(df_pd[df_pd["diabetes_binary"] == 0][name_feature], alpha=0.5, fill=True, color="#FF0000", label="No Diabetes", ax=ax)
    	sns.kdeplot(df_pd[df_pd["diabetes_binary"] == 1][name_feature], alpha=0.5, fill=True, color="#00FF00", label="Diabetes", ax=ax)
    	sns.kdeplot(df_pd[name_feature], alpha=0.5, fill=True, color="#0000FF", label="Total", ax=ax)
    	ax.set_xlabel(name_feature)
    	ax.set_ylabel("")
    	ax.legend(loc='best')
    	plt.savefig('output/' + name_feature + '.png', transparent=True, facecolor='white')
    	plt.close()
    for feat in num_feat:
    	plotContinuousChart(feat)

	
    # Correlation heatmmap
    plt.figure(figsize=(25,18))
    cor = df_pd.corr()
    chart = sns.heatmap(cor, annot=True, cmap=plt.cm.Reds, fmt='.2f')
    chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
    chart.set_yticklabels(chart.get_yticklabels(), rotation=45, verticalalignment='top')
    plt.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.15)
    plt.savefig('output/correlation.png', transparent=True)


    ############################################
    ###### Balancing unbalanced dataset ########
    ############################################
    df_size = df_unbalanced.count()

    # Undersampling dataframe portion with "diabetes_binary" = 1
    minor_df = df_unbalanced.filter(col("diabetes_binary") == 1)
    minor_df_size = minor_df.count()
    minor_ratio = int((df_size/2)/minor_df_size)
    a = range(minor_ratio)
    oversampled_df = minor_df.withColumn("dummy", explode(array([lit(x) for x in a]))).drop('dummy')

    # Oversampling dataframe portion with "diabetes_binary" = 0
    major_df = df_unbalanced.filter(col("diabetes_binary") == 0)
    major_df_size = df_size-minor_df_size
    major_ratio = int(major_df_size/(df_unbalanced.count()/2))
    undersampled_df = major_df.sample(False, 1/major_ratio)

    # Merging undersampled and oversampled dataframe
    unbalancing_ratio = major_df_size/minor_df_size
    df = oversampled_df.unionAll(undersampled_df)


    ############################################
    ######### Creating ML pipeline #############
    ############################################
    
    continuousFeatures = [col for col in df.columns if col != "diabetes_binary"]
    # Assembler for continuous features
    continuousAssembler = VectorAssembler(inputCols = continuousFeatures, outputCol = "assembledFeatures")

    # Scales all continuous features to be in the range [0,1]
    continuousScaler = MinMaxScaler(inputCol = "assembledFeatures", outputCol = "normalizedFeatures")

    

    # Assembl all features in 'final_features'
    input = ['normalizedFeatures']
    totalAssembler = VectorAssembler(inputCols = input, outputCol = "final_features")

    # Logistic regression
    regressor = LogisticRegression(featuresCol = "final_features", labelCol = "diabetes_binary")

    # Inizializing pipeline 
    stages = [continuousAssembler, continuousScaler, totalAssembler, regressor]
    pipeline = Pipeline(stages = stages)



    ############################################
    ########## training pipeline model #########
    ############################################
    # Splitting dataset into traing and set datasets
    train_set_un, test_set_un = df.randomSplit([0.7,0.3])
    df_persist = df.persist()
    train_set = train_set_un.persist()
    test_set = train_set_un.persist()

    # Model training
    pipeline_model = pipeline.fit(train_set)

    # Making predictions
    predictions = pipeline_model.transform(test_set)

    # Printing confusion matrix
    sns.set(font_scale=3)
    y_true = predictions.select(['diabetes_binary']).collect()#aggiungo la colonna diabets_binary
    y_pred = predictions.select(['prediction']).collect()
    confusion_matrix = metrics.confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(15, 10))
    sns.heatmap(confusion_matrix, xticklabels=['No', 'Yes'], yticklabels=['No', 'Yes'], annot=True, cmap=plt.cm.Blues, fmt='d')
    plt.xlabel('Predicted values')
    plt.ylabel('Real values')
    plt.subplots_adjust(top=0.96, bottom=0.15)
    plt.savefig('output/confusionMatrix.png', transparent=True)

    # Accuracy computation
    eval = MulticlassClassificationEvaluator(labelCol="diabetes_binary", predictionCol="prediction", metricName="accuracy")
    accuracy = eval.evaluate(predictions)

    # Training pipeline model with entire dataset
    pipeline_model = pipeline.fit(df_persist)



    ############################################
    ####### exporting pmml pipeline model ######
    ############################################
    PMMLBuilder(sc, df_persist, pipeline_model).buildFile("output/Diabetes.pmml")
    os = Openscoring("http://localhost:8080/openscoring")

    # Shall be available at http://localhost:8080/openscoring/model/HeartDisease
    os.deployFile("Diabetes", "output/Diabetes.pmml")

    print('')
    print('')
    print('####################################################################################################')
    print('####################################################################################################')
    print('####################################################################################################')
    print('########  --> Rapporto non-diabetici/diabetici nel dataset: %.3f                          ##########' %unbalancing_ratio)
    print('########  --> Estimator: logistic regression                                              ##########')
    print('########  --> Evaluator: MulticlassClassificationEvaluator                                ##########')
    print('########  --> Prediction accurancy: %.3f                                                  ##########' %accuracy)
    print('########  --> per visitare il Client visitare: client/homePage.html                       ##########')
    print('########  --> Risultati prediction: http://localhost:8080/openscoring/model/Diabetes      ##########')
    print('####################################################################################################')
    print('####################################################################################################')
    print('####################################################################################################')
    print('')
    print('')

except Exception:
    traceback.print_exc()

    

############################################
############### stopping Spark #############
############################################
sc.stop()
