# from pathlib import Path
#
# base_path = Path(__file__).parent
# with open(f"{base_path}/")
from sqlalchemy import create_engine
import mysql.connector
def connect():
	cnx = mysql.connector.connect(user="", password="", host="", port=3306, database="")
	
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
	connect()