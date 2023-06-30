#!/bin/bash 

#STOPPING CASSANDRA SERVICE
sudo service cassandra stop

#REMOVING TEMP DIRECTORIES
rm -r /~
rm -r /nohup.out

#STOPPING OPENSCORING SERVER
pkill -f lib/openscoring-server-executable-2.1.1.jar

#STOPPING ENDPOINT FOR INSERTION
pkill -9 -f addEndPoint.py
