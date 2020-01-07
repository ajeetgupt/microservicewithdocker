import sys
import logging
import rds_config
import pymysql
import json
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_cors import CORS, cross_origin
from datetime import date
from datetime import datetime
#rds settings

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = False

def RdsConnection():
    rds_host  = "database-fsd-sample.cniw8p6tx7sx.us-east-1.rds.amazonaws.com"
    name = rds_config.db_username
    password = rds_config.db_password
    db_name = rds_config.db_name
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    try:
            conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
            logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
            logger.error(e)
            sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
    return conn.cursor()

def calculateAge(birthDate): 
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 
    return age

@app.route('/', methods=['GET'])
def NumberOfRow():
    cursor=RdsConnection()
    cursor.execute(""" SELECT * FROM PremiumTable """)
        # fetch all of the rows from the query
    records = cursor.fetchall ()
    #print("Total number of rows in is: ", cursor.rowcount)
    return jsonify(cursor.rowcount)

@app.route('/viewpolicy', methods=['POST'])
def ViewPolicy():
    if not request.json:
        abort(400)
    dob= request.json["data"]["input_main"]["dob"]
    cust_name=request.json["data"]["cust_name"]
    date_object = datetime.strptime(dob,'%Y/%m/%d').date()
    age=calculateAge(date_object)
    sql_query1 = """select Id from SourceTable where From_age=%s and Till_age=%s and Disease=%s and City=%s""" 
    if age >=20 and age <=30:
        data_tuple1=(20, 30, request.json["data"]["input_main"]['disease'], request.json["data"]["input_main"]['city'])
    elif age > 30 and age <=40:
        data_tuple1=(30, 40, request.json["data"]["input_main"]['disease'], request.json["data"]["input_main"]['city'])
    elif age > 40 and age <=50:
        data_tuple1=(40, 50, request.json["data"]["input_main"]['disease'], request.json["data"]["input_main"]['city']) 
    elif age > 50 and age <=60:
        data_tuple1=(50, 60, request.json["data"]["input_main"]['disease'], request.json["data"]["input_main"]['city'])

    cursor=RdsConnection()
    cursor.execute(sql_query1, data_tuple1)
    # fetch all of the rows from the query
    records = cursor.fetchall ()
    data_tuple2=(records[0])
    sql_query2= """select PlanType, Policy_limit_InLakh, Monthly_Premium, Deductible from PremiumTable where Source_ID=%s"""
    cursor.execute(sql_query2, data_tuple2)
    row_headers=[x[0] for x in cursor.description]
    rv = cursor.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return jsonify(json_data)

if __name__=="__main__":
    # numberofrow()
    app.run(host='0.0.0.0', port='8080')
