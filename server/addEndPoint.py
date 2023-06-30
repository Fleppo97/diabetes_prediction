from flask import Flask
from flask import request
import pyspark
from pyspark.sql.functions import col,isnan,when,count,explode,array,lit
import json
from datetime import datetime
from cassandra.cluster import Cluster

app = Flask(__name__)
cluster = Cluster()
session = cluster.connect('diabetes_dataset', wait_for_all_pools=True)

@app.route('/insert', methods=['POST'])
def add_income():
    paramList = request.get_json()
    arg = [i for i in paramList['arguments'].values()]
    print(arg)
    query = "INSERT INTO features (id, diabetes_binary, highbp, highchol, cholcheck, bmi, smoker, stroke, heartdiseaseorattack, physactivity, fruits, veggies, hvyalcoholconsump, anyhealthcare, nodocbccost, genhlth, menthlth, physhlth, diffwalk, sex, age, education, income) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    response = {'message': 'Dati inseriti correttamente'}
    return json.dumps(response), 200

app.run()
