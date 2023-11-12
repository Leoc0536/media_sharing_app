import mysql.connector
from sqlalchemy import create_engine

def connect():
	username = input("")
	password = input("")
	cnx = mysql.connector.connect(user=username, password=password, host="", port=3306, database="")

	print(cnx)
	cursor = cnx.cursor()
	print("getting tables")
	cursor.execute("show tables;")
	print("result: ")
	result = cursor.fetchall()
	print(result)
	print(len(result))
	print("close")
	# cursor.close()