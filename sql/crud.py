from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from . import schemas, models
from .models import Media, Keyword
from .database import engine
import pandas as pd
from pathlib import Path


def get_media():
	path = Path(__file__).parent
	with open(f"{path}/sql_script/test.sql") as f:
		sql = f.read()
	df = pd.read_sql_query(sql, engine)
	df.head()
	return df.to_dict(orient="records")


def get_media_by_name(db: Session, media_name: str):
	return db.query(models.Media).filter(models.Media.name == media_name).first()


def get_media_by_keyword(db: Session, keyword: str):
	db.query(Keyword.owner_id)
	return None


def get_items(db: Session):
	return db.query(models.Keyword).all()


def create_media_keyword(db: Session, keyword: schemas.Keyword, user_id: int):
	
	db_keyword = models.Keyword(**keyword.model_dump(), owner_id=user_id)
	db.add(db_keyword)
	db.commit()
	db.refresh(db_keyword)
	return db_keyword