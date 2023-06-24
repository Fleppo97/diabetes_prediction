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

# Caricamento dei dati da Cassandra
df_unbalanced = spark.read.format('org.apache.spark.sql.cassandra') \
    .option('table', 'features') \
    .option('keyspace', 'diabetes_dataset') \
    .load()

    
sc = spark.sparkContext

try:
    print("#"*200)
    print("CARICO CASSANDRA")
    
    df_unbalanced = spark.read.format("org.apache.spark.sql.cassandra") \
    .option("table", "features") \
    .option("keyspace", "diabetes_dataset") \
    .option("partitioner", "org.apache.spark.sql.cassandra.DefaultSource") \
    .option("spark.cassandra.auth.username", "cassandra") \
    .option("spark.cassandra.auth.password", "cassandra") \
    .load()          #non funziona con spark 3.3 quindi lo cancello e installo 3.2.2

    
    # Creating spark dataframe from Cassandra db 
    #df_unbalanced= #spark.read.format("org.apache.spark.sql.cassandra").options(table="features",keyspace="diabetes_dataset").load()
 #   df_unbalanced= df_unbalanced.drop("id")
  #  df_pd = df_unbalanced.toPandas()
    print("#"*200)
    print("OPERAZIONE RIUSCITA")
    print("#"*200)
    print(df_unbalanced.count())
    print("#"*200)

    ############################################
    ###### Anlizing dataset with charts ########
    ############################################
    # Setting Seaborn features
    sns.set(font_scale=2)
    sns.set_style("darkgrid")


    # Selecting features
    features = ["diabetes_binary", "highbp", "highchol", "cholcheck", "bmi", "smoker", "stroke", "heartdiseaseorattack", "physactivity", "fruits", "veggies", "hvyalcoholconsump", "anyhealthcare", "nodocbccost", "genhlth", "menthlth", "physhlth", "diffwalk", "sex", "age", "education", "income"]
    

    df_pd = df_unbalanced.toPandas()

    # Create features charts
    def plotContinuousChart(xLabel):
    	fig, ax = plt.subplots(figsize=(25, 9))
    	sns.kdeplot(df_pd[df_pd["diabetes_binary"] == 0][xLabel], alpha=0.5, fill=True, color="#4285f4", label="No Diabetes", ax=ax)
    	sns.kdeplot(df_pd[df_pd["diabetes_binary"] == 1][xLabel], alpha=0.5, fill=True, color="#ea4335", label="Diabetes", ax=ax)
    	sns.kdeplot(df_pd[xLabel], alpha=0.5, fill=True, color="#008000", label="Total", ax=ax)
    	ax.set_xlabel(xLabel)
    	ax.set_ylabel("Number among respondents")
    	ax.legend(loc='best')
    	plt.savefig('output/' + xLabel + '.png', transparent=True)

    for feat in features:
    	plotContinuousChart(feat)



    # Correlation heatmmap1
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
    print(minor_df_size)
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
    

    # Assembler for continuous features: all the continuous features have to be assembled as a vector in the same column to be scaled
    continuousAssembler = VectorAssembler(inputCols = features, outputCol = "assembledFeatures")

    # Scaler: scales all continuous features (assembled in column 'assembledFeatures') to be in the range [0,1]
    continuousScaler = MinMaxScaler(inputCol = "assembledFeatures", outputCol = "normalizedFeatures")

    

    # Assembler for all features: all the features are assembled in the 'final_features' column
    input = []
    input.append('normalizedFeatures')
    totalAssembler = VectorAssembler(inputCols = input, outputCol = "final_features")

    # Logistic regression: suitable for categorical and noncontinuous decisions
    regressor = LogisticRegression(featuresCol = "final_features", labelCol = "heartdisease_indexed")

    # Inizializing pipeline ('categoricalIndexer' is already a list, so it must be concatenated with the list of remaining stages)
    stages = categoricalIndexer + [categoricalEncoder, continuousAssembler, continuousScaler, totalAssembler, regressor]
    pipeline = Pipeline(stages = stages)



    ############################################
    ########## training pipeline model #########
    ############################################
    # Splitting dataset into traing and set datasets
    print("#"*200)
    print("TRAIN MODEL")
    train_set_un, test_set_un = df.randomSplit([0.7,0.3])
    df_persist = df.persist()
    train_set = train_set_un.persist()
    test_set = train_set_un.persist()
    print("#"*200)
    print("FIT MODEL")

    # Model training
    pipeline_model = pipeline.fit(train_set)
    print("#"*200)

    # Making predictions
    predictions = pipeline_model.transform(test_set)

    # Printing confusion matrix
    sns.set(font_scale=3)
    y_true = predictions.select(['diabetes_indexed']).collect()
    y_pred = predictions.select(['prediction']).collect()
    confusion_matrix = metrics.confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(15, 10))
    sns.heatmap(confusion_matrix, xticklabels=['No', 'Yes'], yticklabels=['No', 'Yes'], annot=True, cmap=plt.cm.Blues, fmt='d')
    plt.xlabel('Predicted values')
    plt.ylabel('Real values')
    plt.subplots_adjust(top=0.96, bottom=0.15)
    plt.savefig('output/confusion.png', transparent=True)

    # Accuracy computation
    eval = MulticlassClassificationEvaluator(labelCol="diabetes_indexed", predictionCol="prediction", metricName="accuracy")
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



    ############################################
    ######## printing info in consolle #########
    ############################################
    print('')
    print('')
    print('####################################################################################################')
    print('####################################################################################################')
    print('####################################################################################################')
    print('########  --> Unbalancing ratio: %.3f                                                   ##########' %unbalancing_ratio)
    print('########  --> Balanced by by keeping the same size of original input dataset              ##########')
    print('########  --> Estimator: logistic regression                                              ##########')
    print('########  --> Evaluator: MulticlassClassificationEvaluator                                ##########')
    print('########  --> Prediction accurancy: %.3f                                                 ##########' %accuracy)
    print('########  --> Prediction served on: http://localhost:8080/openscoring/model/Diabetes  ##########')
    print('########  --> Client page: ../Client/homePage.html                                     ##########')
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
