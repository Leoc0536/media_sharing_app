import uvicorn
from fastapi import FastAPI, Request, Depends, status, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException
# from blob_connector import BlobConnector
from typing import Annotated
from sql.database import engine, SessionLocal
from sqlalchemy.orm import Session
from sql.schemas import Media, Keyword
from sql import models, crud
from flask import Flask, request, redirect, render_template
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv


app = FastAPI(description="Sample FastAPI App")

models.Base.metadata.create_all(bind=engine)

template = Jinja2Templates(directory="template")


def get_db():
    db = SessionLocal()
    try:
        yield db
        print("db activated")
    finally:
        db.close()


db_dependancy = Annotated[Session, Depends(get_db)]


@app.get("/", tags=["main", "testing"])
async def root():
    return {"message": "Hello World!!!"}


@app.get("/helloworld/{name}", response_class=HTMLResponse)
async def say_hello(request: Request, name: str):
    return template.TemplateResponse("index.html", {"request": request, "name": name})


# @app.get("/azure-blob")
# async def create_upload_file():
#     blob = BlobConnector()
#     blob.connect()
load_dotenv()
storage_account_key = os.getenv('storage_account_key')
storage_account_name = os.getenv('storage_account_name')
connection_string = os.getenv('connection_string')
container_name = os.getenv('container_name')



@app.post("/azure-photo")
async def create_upload_file(name: str = Form(...), file: UploadFile = File(...), database: Session = Depends(get_db)):
    if not file:
        return {"message": "No upload file sent"}
    else:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=name)

        try:
            contents = file.file.read()
            file.file.seek(0)
            blob_client.upload_blob(contents)
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            file.file.close()

        return {
            'message': 'File uploaded successfully to Azure Cloud'
        }


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

# @app.get('/display-page')
# def display():
	# blob = BlobConnector()
	# container = blob.connect()
	# blob_items = container.list_blobs()
	# images = []
	# videos = []
	# for blob in blob_items:
	# 	blob_client = container.get_blob_client(blob=blob.name)
	# 	if blob.name.endswith(('.png', '.jpeg', '.jpg', '.gif')):
	# 		images.append(blob_client.url)
	# 	elif blob.name.endswith(('.mp4', '.webm', '.ogg')):
	# 		videos.append(blob_client.url)
	# image, video = []
	# return render_template('displayPage.html', images=images, videos=videos)
	

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


@app.post("/medias/{user_id}/keyword", status_code=status.HTTP_201_CREATED)
async def create_media(keyword: Keyword, user_id: int, db: Session = Depends(get_db)):
    keyword = crud.create_media_keyword(db, keyword=keyword, user_id=user_id)
    return keyword


@app.get("/medias/{media_name}")
def get_media_by_name(media_name: str, db: Session = Depends(get_db)):
    keyword = crud.get_media_by_name(db, media_name=media_name)
    return keyword


@app.get("/medias/{keyword}/", tags=["media"])
def get_media_by_keyword(keyword: str, db: Session = Depends(get_db)):
    keyword_list = crud.get_media_by_keyword(keyword)
    return keyword_list


@app.get("/medias/", response_class=HTMLResponse, tags=["media", "view"])
def read_medias(request: Request, ):
    medias = crud.get_media()
    print(medias)
    return template.TemplateResponse("index.html", {"request": request, "medias": medias})


if __name__ == '__main__':
    uvicorn.run('app.main:app')
