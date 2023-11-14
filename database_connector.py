import mysql.connector
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

class MySQLConnector:
	def __init__(self):
		load_dotenv()
	def connect(self):
		username = os.getenv("db_username")
		password = os.getenv("password")
		host = os.getenv("host")
		database = os.getenv('database')
		cnx = mysql.connector.connect(user=username, password=password, host=host, port=3306, database=database)
	
		print(cnx)
		cursor = cnx.cursor()
		print("getting tables")
		cursor.execute("show tables;")
		print("result: ")
		result = cursor.fetchall()
		print(result)
		print(len(result))
		print("close")
		cursor.close()
	
if __name__ == '__main__':
    connector = MySQLConnector()
    connector.connect()