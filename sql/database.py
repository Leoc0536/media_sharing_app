# import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
username = os.getenv("db_username")
# username = 'springadmin'
password = os.getenv("password")
# password = 'Hdds2401'
host = os.getenv("host")
# host = 'hdds2401-leo.mysql.database.azure.com'
database = os.getenv('database')
# database = 'testing'
URL_DATABASE = f"mysql+pymysql://{username}:{password}@{host}:3306/{database}"

engine = create_engine(URL_DATABASE, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# class MySQLConnector:
# 	def connect(self):
#
#
# 		load_dotenv()
# 		username = os.getenv("db_username")
# 		password = os.getenv("password")
# 		host = os.getenv("host")
# 		database = os.getenv('database')
# 		try:
# 			cnx = mysql.connector.connect(user=username, password=password, host=host, port=3306, database=database)
# 			cursor = cnx.cursor()
# 			print("getting tables")
# 			cursor.execute("show tables;")
# 			result = cursor.fetchall()
# 			print(f"{result= }")
#
# 			cursor.execute("select * from t;")
# 			result = cursor.fetchall()
# 			print(f"{result= }")
			#
			# print("close")
			# cursor.close()
		#
		# except mysql.connector.errors.ProgrammingError as e:
		# 	print(e)
		# finally:
		# 	print("end")
#
#
# if __name__ == '__main__':
# 	connector = MySQLConnector()
# 	connector.connect()
#