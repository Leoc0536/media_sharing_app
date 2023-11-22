from sqlalchemy.orm import Session
from . import schemas, models
from .models import Media, Keyword
from .database import engine
import pandas as pd
from pathlib import Path


def get_media_record():
	path = Path(__file__).parent
	with open(f"{path}/sql_script/test.sql") as f:
		sql = f.read()
	df = pd.read_sql_query(sql, engine)
	if df.size < 1:
		df = pd.read_sql_query("SELECT * FROM media_metadata;", engine)
	df.head()
	return df.to_dict(orient="records")


def get_media_name(media_id: int, db: Session):
	record = db.query(models.Media).filter(models.Media.id == media_id).first()
	return record.name if record else f"ID {media_id} does not exist"


def get_media_by_name(db: Session, media_name: str):
	path = Path(__file__).parent
	with open(f"{path}/sql_script/select_by_name.sql") as f:
		sql = f.read()
		sql = sql.replace('{media_name}', f'{media_name}')
	df = pd.read_sql_query(sql, engine)
	df.head()
	return df.to_dict(orient="records")
	# return db.query(models.Media, Keyword).join(Keyword).filter(models.Media.name == media_name).all()


def get_media_by_id(db: Session, media_id: int):
	result = db.query(Media).filter(Media.id==media_id).first()
	return result


async def change_media_description(db: Session, media_id: int, description: str):
	result = get_media_by_id(db, media_id)
	if result:
		result.description = description
		db.commit()
		return "Update successfully"
	return f"{media_id= } not found"


def delete_media(db: Session, media_id: int):
	remove = db.query(models.Media).filter(models.Media.id==media_id).first()
	remove_key = db.query(Keyword).filter(Keyword.owner_id==media_id).all()
	if remove:
		db.delete(remove)
		for _ in remove_key:
			db.delete(_)
		db.commit()
		return f"Media ID {media_id} removed"
	return f"ID {media_id} does not exist"


def create_media_keyword(db: Session, keyword: schemas.Keyword, owner_id: int):
	db_keyword = models.Keyword(**keyword.model_dump(), owner_id=owner_id)
	db.add(db_keyword)
	db.commit()
	db.refresh(db_keyword)
	return db_keyword
