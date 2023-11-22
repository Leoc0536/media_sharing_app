import uvicorn
from fastapi import FastAPI, Request, Depends, status, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException
# from blob_connector import BlobConnector
from typing import Annotated

import back_end.database
from back_end.database import engine, SessionLocal
from sqlalchemy.orm import Session
from back_end.schemas import Media, Keyword
from back_end import models, crud
from flask import Flask, request, redirect, render_template
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
import time
from datetime import datetime
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

load_dotenv()
storage_account_key = os.getenv('storage_account_key')
storage_account_name = os.getenv('storage_account_name')
connection_string = os.getenv('connection_string')
container_name = os.getenv('container_name')


@app.get("/upload/azure-photo", response_class=HTMLResponse, tags=["upload"])
async def upload_file(request: Request):
    return template.TemplateResponse("uploadPage.html", {"request": request})


@app.post("/upload/azure-photo", tags=["upload"])
async def create_upload_file(description: str = Form(...), keyword: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_name = file.filename
    if get_media_by_name(file_name, db):
        return f"Duplicate entry '{file_name}'"
    if not file:
        return {"message": "No upload file sent"}
    else:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        # object_url = blob_client.url
        try:
            contents = file.file.read()
            file.file.seek(0)
            blob_client.upload_blob(contents)
            object_url = blob_client.url
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            file.file.close()
        
    media = Media(
      name=file_name,
      description=description,
      date_of_media=datetime.now(),
      object_url=object_url
    )
    await create_media(media, keyword, db)
    return RedirectResponse("/medias", 303)
    

# @app.post("/medias/", status_code=status.HTTP_201_CREATED)
async def create_media(media: Media, keyword: str, db: Session = Depends(get_db)):
    db_media = models.Media(**media.model_dump())
    db.add(db_media)
    print(db_media.name)
    print(db_media.description)
    print(db_media.date_of_media)
    db.commit()
    keyword = Keyword(keyword=keyword, owner_id=db_media.id)
    await create_media_keyword(keyword, db_media.id, db)
    
    
@app.patch("/medias/{media_id}/description", tags=["media"])
async def change_media_description(media_id: int, description: str, db: Session = Depends(get_db)):
    return await crud.change_media_description(db=db, media_id=media_id, description=description)


@app.post("/medias/{media_id}/keyword", tags=["media"])
async def create_media_keyword(keyword: Keyword, media_id: int, db: Session = Depends(get_db)):
    media = crud.get_media_by_id(db, media_id)
    if media:
        keyword = crud.create_media_keyword(db, keyword=keyword, owner_id=media_id)
        return keyword
    return f"{media_id} Does not exist"

@app.get("/medias/{media_name}", tags=["media"])
def get_media_by_name(media_name: str, db: Session = Depends(get_db)):
    media = crud.get_media_by_name(db, media_name=media_name)
    return media


@app.get("/medias/keyword/{keyword}/", tags=["media"])
def get_media_by_keyword(keyword: str, request: Request, db: Session = Depends(get_db)):
    medias = crud.get_media_by_keyword(db=db, keyword=keyword)
    return template.TemplateResponse("displayPage.html", {"request": request, "medias": medias})


@app.get("/medias/", response_class=HTMLResponse, tags=["media"])
def read_medias(request: Request):
    medias = crud.get_media_record()
    print(medias)
    return template.TemplateResponse("displayPage.html", {"request": request, "medias": medias})

@app.delete("/medias/{media_id}", tags=["media"])
async def delete_media(media_id: int, db: Session = Depends(get_db)):
    media_name = crud.get_media_name(media_id, db)
    connector = BlobServiceClient.from_connection_string(connection_string)
    connector.get_blob_client(container_name, blob=media_name).delete_blob()
    return crud.delete_media(db=db, media_id=media_id)


@app.get("/login", tags=["login"], response_class=HTMLResponse)
def login(request: Request):
    return template.TemplateResponse("loginPage.html", {"request": request})
   

@app.post("/login", tags=["login"])
async def login(request: Request, username: str = Form(), password: str = Form()):
    print(f"{username= }")
    print(f"{password= }")
    credentials = {"username": username, "password": password}
    if check_credentials(credentials) == "Logged in!":
        return RedirectResponse("/medias", 303)
    

def check_credentials(credentials: dict):
    return back_end.database.login(**credentials)


if __name__ == '__main__':
    uvicorn.run('app.main:app')
