import os
import json
import time
import dotenv
from dotenv import load_dotenv
from flask import request, Response, Flask, render_template, jsonify
import mysql.connector
from mysql.connector import errorcode


application = Flask(__name__)
app = application

# https://pybit.es/persistent-environment-variables.html
load_dotenv()

def get_db_creds():
    db = os.getenv("DB", None) or os.environ.get("database", None)
    username = os.getenv("USER", None) or os.environ.get("username", None)
    password = os.getenv(
        "PASSWORD", None) or os.environ.get("password", None)
    hostname = os.getenv("HOST", None) or os.environ.get("dbhost", None)
    return db, username, password, hostname


def instantiate_db_connection():
    db, username, password, hostname = get_db_creds()
    try:
        cnx = mysql.connector.connect(user=username, password=password,
                                      host=hostname,
                                      database=db)
    except Exception as exp:
        print(exp)
        raise

    if cnx:
        return cnx

def create_table():
    # Check if table exists or not. Create and populate it only if it does not exist.
    # https://www.w3schools.com/sql/sql_create_table.asp
    table_ddl = 'CREATE TABLE pool( pool_name VARCHAR(255) NOT NULL, status VARCHAR(255) NOT NULL, phone VARCHAR(255) NOT NULL, pool_type VARCHAR(255) NOT NULL, PRIMARY KEY (pool_name))'
    
    cnx = instantiate_db_connection()
    cur = cnx.cursor()

    try:
        # transaction
        cur.execute(table_ddl)
        # comtting the transaction
        cnx.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            # rollback the trasaction
            cnx.rollback()
            print(err.msg)

def query_data(pool_name=None):
    cnx = instantiate_db_connection()
    cur = cnx.cursor(dictionary=True)
    if pool_name:
        # https://pynative.com/python-mysql-select-query-to-fetch-data/
        check_for_pool = """select * from pool where pool_name = %s"""
        try:
            cur.execute(check_for_pool, (pool_name,))
            record = cur.fetchone()
            return record
        except mysql.connector.Error as err:
            cnx.rollback()
            print(err.msg)
        
    else:
        # https://pynative.com/python-mysql-select-query-to-fetch-data/
        check_for_pool = "select * from pool" 
        try:
            cur.execute(check_for_pool)
            record = cur.fetchall()
            return record
        except mysql.connector.Error as err:
            cnx.rollback()
            print(err.msg)
        

def modify_db(record, put=False, post=False, delete=False):
    pool = record
    pool_name = pool['pool_name']
    # https://www.pythoncentral.io/convert-dictionary-values-list-python/
    pool_values = list(pool.values())
    cnx = instantiate_db_connection()
    cur = cnx.cursor()

    if post == True:
        try:
            # https://pynative.com/python-mysql-insert-data-into-database-table/
            mySql_insert_query = """INSERT INTO pool (pool_name, status, phone, pool_type)
                                VALUES (%s, %s, %s, %s) """
            cur.execute(mySql_insert_query, pool_values)
        except mysql.connector.Error as err:
            cnx.rollback()
            print(err.msg)
        
    if put == True:
        # https://pynative.com/python-mysql-update-data/
        pool_values.append(pool_name)
        sql_update_query = """Update Pool set pool_name = %s, status = %s, phone = %s, pool_type = %s where pool_name = %s"""
        try:
            cur.execute(sql_update_query, pool_values)
        except mysql.connector.Error as err:
            cnx.rollback()
            print(err.msg)

    if delete == True:
        # https://pynative.com/python-mysql-delete-data/
        sql_delete_query = """Delete from Pool where pool_name = %s"""
        try:
            cur.execute(sql_delete_query, (pool_name,))
        except mysql.connector.Error as err:
            print(err.msg)
            cnx.rollback()

    cnx.commit()

@app.route("/static/add_pool", methods=['POST'])
def add_pool():

    pool = {}
    pool['pool_name'] = request.form['poolName']
    pool['status'] = request.form['status']
    pool['phone'] = request.form['phone']
    pool['pool_type'] = request.form['poolType']
    
    
    # Insert into database.

    modify_db(pool, post=True)

    return render_template('pool_added.html')


@app.route("/pools")
def get_pools():
    response = {}
    pools = query_data()

    return jsonify(pools)


@app.route("/")
def pool_info_website():
    return render_template('index.html')

try:
    print("---------" + time.strftime('%a %H:%M:%S'))
    print("Before create_table global")
    create_table()
    print("After create_data global")
except Exception as exp:
    print("Got exception %s" % exp)
    conn = None


if __name__ == "__main__":
    app.debug = True
    app.run()
