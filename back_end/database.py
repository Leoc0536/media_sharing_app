import mysql.connector
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

def login(username: str, password: str):
	try:
		cnx = mysql.connector.connect(user=username, password=password, host=host, port=3306, database=database)
		cursor = cnx.cursor()
		cursor.execute("SHOW tables;")
		cursor.close()

	except mysql.connector.errors.ProgrammingError as e:
		return e
	return "Logged in!"