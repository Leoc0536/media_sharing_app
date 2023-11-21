from fastapi import FastAPI, Request, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from blob_connector import BlobConnector
# from database import MySQLConnector
from pydantic import BaseModel
from typing import Annotated
from sql import models
from sql.database import engine, SessionLocal
from sqlalchemy.orm import Session
from sql.schemas import Media, Keyword
from sql import models, schemas, crud
from flask import Flask, request, redirect, render_template
import ast
import json
import re

app = FastAPI(description="Sample FastAPI App")

models.Base.metadata.create_all(bind=engine)


template = Jinja2Templates(directory="template")

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.get("/", tags=["main"])
async def root():
	return {"message": "Hello World!!!"}
	# return ["Hello", "World"]

@app.get("/hello/{name}", tags=['main'])
async def say_hello(name: int):
	return {"message": f"Hello {name}"}

@app.get("/file/{file_path:path}")
async def read_file(file_path: str):
	return {"file_path": file_path}

item_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# params not part of path will be interpreted as query param
# i.e. /items/?skip0&limit=10
@app.get("/items/")
async def read_item(q: str | None = None):
	results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
	if q:
		results.update({"q": q})
	return results

@app.post("/items/")
async def create_item(item: Item):
	item.name = item.name.capitalize()
	item_dict = item.model_dump()
	return item_dict

@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item):
	return {"item_id": item_id, **item.model_dump()}

@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
	item = {"item_id": item_id}
	if q:
		item.update({"q": q})
	if not short:
		item.update(
			{"description": "This is an amazing item that has a long description"}
		)
	return item

@app.get("/helloworld/{name}", response_class=HTMLResponse)
async def say_hello(request: Request, name: str):
	return template.TemplateResponse("index.html", {"request": request, "name": name})

@app.get("/azure-blob")
async def create_upload_file():
	blob = BlobConnector()
	blob.connect()

@app.get('/upload-page')
def upload_form():
    return render_template('uploadPage.html')

@app.post('/upload-page')
def upload_file():
    file = request.files['media']
    if file:
        file.save(file.filename)
        return 'File uploaded successfully.'
    else:
        return 'No file uploaded.'

@app.get('/display-page')
def display():
	blob = BlobConnector()
	blob.connect()
	blob_items = blob.container_client.list_blobs()
	images = []
	videos = []
	for blob in blob_items:
		blob_client = blob.container_client.get_blob_client(blob=blob.name)
		if blob.name.endswith(('.png', '.jpeg', '.jpg', '.gif')):
			images.append(blob_client.url)
		elif blob.name.endswith(('.mp4', '.webm', '.ogg')):
			videos.append(blob_client.url)
	return render_template('displayPage.html', images=images, videos=videos)
	


def get_db():
	# mysql = MySQLConnector()
	# mysql.connect()
	db = SessionLocal()
	try:
		yield db
		print("db activated")
	finally:
		db.close()
		
db_dependancy = Annotated[Session, Depends(get_db)]
@app.post("/medias/", status_code=status.HTTP_201_CREATED)
async def create_media(media: Media, db: db_dependancy):
	db_media = models.Media(**media.model_dump())
	# db_media.keyword = str(db_media.keyword)
	print(db_media.name)
	print(db_media.description)
	print(db_media.date_of_media)
	# print(db_media.keyword)
	print(db_media.object_url)
	db.add(db_media)
	db.commit()


@app.post("/media/{user_id}/keyword", status_code=status.HTTP_201_CREATED)
async def create_media(keyword: Keyword, user_id: int, db: Session = Depends(get_db)):
	keyword = crud.create_media_keyword(db, keyword=keyword, user_id=user_id)
	return keyword

@app.get("/media/{media_name}")
def get_media_by_name(media_name: str, db: Session = Depends(get_db)):
	keyword = crud.get_media_by_name(db, media_name=media_name)
	return keyword


@app.get("/media/get/")
def get_media_by_keyword():
	keyword_list = crud.get_media_by_keyword()
	return keyword_list


@app.get("/medias/")
def read_medias():
	medias = crud.get_media()
	return medias


if __name__ == '__main__':
	uvicorn.run('app.main:app')
