# from pathlib import Path
#
# base_path = Path(__file__).parent
# with open(f"{base_path}/")
from sqlalchemy import create_engine
import mysql.connector
def connect():
	cnx = mysql.connector.connect(user="springadmin", password="Hdds2401", host="hdds2401-leo.mysql.database.azure.com", port=3306, database="mysql")
	
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