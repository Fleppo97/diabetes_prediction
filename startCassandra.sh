#!/bin/bash

#EXPORTING PYTHON, HADOOP AND SPARK DIR VARIABLES
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=python3
export HADOOP_DIR=/home/bigdata2022/hadoop-3.3.4
export SPARK_HOME=/home/bigdata2022/spark-3.3.0
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin:$HADOOP_DIR/bin:$HADOOP_DIR/sbin

#STOPPING HADOOP
$HADOOP_DIR/sbin/stop-dfs.sh
$HADOOP_DIR/sbin/stop-yarn.sh

#RUNNING HADOOP
$HADOOP_DIR/sbin/start-dfs.sh
$HADOOP_DIR/sbin/start-yarn.sh
jps
$HADOOP_DIR/bin/hdfs dfsadmin -safemode leave

#CREATE DIRECTORY IN HDFS
$HADOOP_DIR/bin/hdfs dfs -mkdir -p hdfs://localhost:9000/Input

#DELETING INPUT IN HDFS
$HADOOP_DIR/bin/hdfs dfs -rm -r /Input/diabetes_database.csv

#LOADING INPUT IN HDFS
$HADOOP_DIR/bin/hdfs dfs -put ./res/input/diabetes_database.csv hdfs://localhost:9000/Input/

#GIVING THE RIGHT PERMISSION
$HADOOP_DIR/bin/hdfs dfs -chmod 750 /Input/diabetes_database.csv



echo "Press enter to go to first step --> Start Cassandra"
read continue
#STARTING CASSANDRA SERVICE
sudo service cassandra start



#CREATING DB AND TABLE
cqlsh < ./start.cql

echo
echo "Press enter to go to last step --> PreProcessing"
read continue

#PRE-PROCESSING DATASET AND INSERTING IN TABLE
$SPARK_HOME/bin/spark-submit --packages com.datastax.spark:spark-cassandra-connector_2.12:3.2.0 --deploy-mode client  --driver-memory 3g  --executor-memory 3g  --executor-cores 2  --queue default ./preProcess.py

echo
echo "Press enter to go to last step --> stop Cassandra"
read continue

#STARTING CASSANDRA SERVICE
sudo service cassandra stop

#STOPPING HADOOP
$HADOOP_DIR/sbin/stop-dfs.sh
$HADOOP_DIR/sbin/stop-yarn.sh
