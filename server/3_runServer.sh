#!/bin/bash 

#EXPORTING PYTHON, HADOOP AND SPARK DIR VARIABLES
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=python3
export HADOOP_DIR=/home/bigdata2022/hadoop-3.3.4
export SPARK_HOME=/home/bigdata2022/spark-3.2.2
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin:$HADOOP_DIR/bin:$HADOOP_DIR/sbin

#STOPPING HADOOP
$HADOOP_DIR/sbin/stop-dfs.sh
$HADOOP_DIR/sbin/stop-yarn.sh

#RUNNING HADOOP
$HADOOP_DIR/sbin/start-dfs.sh
$HADOOP_DIR/sbin/start-yarn.sh
jps

#DELETING INPUT/OUTPUT DIRECTORY IN HDFS AND LOCAL
rm -r output/*

$HADOOP_DIR/bin/hdfs dfsadmin -safemode leave

#STARTING CASSANDRA SERVICE
sudo service cassandra start

#LAUNCHING THE OPENSCORING SERVER ON http://localhost:8080/openscoring
java -jar lib/openscoring-server-executable-2.1.1.jar &

#SETTING SPARK AND CREATE PREDICTION MODEL
$SPARK_HOME/bin/spark-submit --packages com.datastax.spark:spark-cassandra-connector_2.12:3.2.0,org.jpmml:pmml-sparkml:2.2.0,org.jpmml:pmml-sparkml-lightgbm:2.2.0,org.jpmml:pmml-sparkml-xgboost:2.2.0  --conf spark.sql.extensions=com.datastax.spark.connector.CassandraSparkExtensions --master yarn  --deploy-mode client  --driver-memory 3g  --executor-memory 3g  --executor-cores 2  --queue default ./model.py


#CREATING ENDPOINT TO INSERT 
FLASK_APP=addEndPoint.py flask run -p 5002 &


#STARTING CLIENT INSTANCE IN GOOGLE CHROME AND DISABLING CHROME SECURITY
nohup google-chrome --disable-web-security --allow-file-access-from-files --user-data-dir=~/chromeTemp ../client/homePage.html &

#STOPPING HADOOP
$HADOOP_DIR/sbin/stop-dfs.sh
$HADOOP_DIR/sbin/stop-yarn.sh
