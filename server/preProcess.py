import pkg_resources
import pyspark
from pyspark.sql.functions import col #######test######
from pyspark.sql import SparkSession
from pyspark.sql.functions import col,isnan,when,count,explode,array,lit,monotonically_increasing_id

# Creating spark session and context
spark=SparkSession.builder.appName('DiabetesPreProcessing').getOrCreate()
sc = spark.sparkContext

# Creating spark dataframe of input csv file
df = spark.read.csv('hdfs://localhost:9000/Input/diabetes_database.csv', inferSchema = True, header = True)

# Adding UUID column 'id'
output = df.withColumn("id", monotonically_increasing_id())
#df = df.withColumn("id", col("id").cast("integer")) ###### test#####

# Ordering columns
output_arr = output.select("id","diabetes_binary","highbp","highchol","cholcheck","bmi","smoker","stroke","heartdiseaseorattack",
"physactivity","fruits","veggies","hvyalcoholconsump","anyhealthcare","nodocbccost","genhlth","menthlth","physhlth",
"diffwalk","sex","age","education","income")

# Saving data in Cassandra db
output_arr.write.format("org.apache.spark.sql.cassandra").mode('append').options(table="features", keyspace="diabetes_dataset").save()

# Stopping spark
sc.stop()
