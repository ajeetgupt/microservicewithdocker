import sys
import logging
import pymysql
import rds_config
import json
import requests
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_cors import CORS, cross_origin
#rds settings

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

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
    return conn
@app.route('/', methods=['GET'])
def HealthCheck():
    return jsonify("hello")

@app.route('/storecustdetail', methods=['POST'])
def CustDetail():
    if not request.json:
        abort(400)
    sql_query = """insert into Members(first_name,last_name,gender,date_of_birth,current_address,postal_address,contact_number,email,occupation,disease,city,income) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    data_tuple=(request.json["firstname"],request.json["lastname"],request.json["gender"], request.json["dob"], request.json["current_address"],request.json["postal_address"],request.json["contact_number"],request.json["email"],request.json["occupation"],request.json["disease"],request.json["city"],request.json["income"])
    conn=RdsConnection()
    cursor=conn.cursor()
    cursor.execute(sql_query, data_tuple)
    conn.commit()
    #print("affected rows = {}".format(cursor.rowcount))
    main_input=request.json
    print(main_input)
    url = 'https://lmfts-viewpolicy-2018254524.us-east-1.elb.amazonaws.com/viewpolicy'
    #print(result_new)
    json_meassage = {
    
    	"msg": "Hi " + request.json["firstname"] + " records successfully inserted in database",
    	"data": {
    	    "input_main":main_input,
    	    "cust_name":request.json["firstname"]
           }
    }
    response = requests.post(url, json=json_meassage, verify=False)
    return jsonify(response.json())

if __name__=="__main__":
    # numberofrow()
    app.run(host='0.0.0.0', port='8080')

