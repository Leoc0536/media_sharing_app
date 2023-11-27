import uvicorn
from fastapi import FastAPI, Request, Depends, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException
import logging
import back_end.database
from back_end.database import engine, SessionLocal
from sqlalchemy.orm import Session
from back_end.schemas import Media, Keyword
from back_end import models, crud
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
from datetime import datetime
app = FastAPI(description="Sample FastAPI App")

models.Base.metadata.create_all(bind=engine)

template = Jinja2Templates(directory="template")
logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_db():
    db = SessionLocal()
    try:
        yield db
        logging.info("db activated")
    finally:
        db.close()
        

load_dotenv()
storage_account_key = os.getenv('storage_account_key')
storage_account_name = os.getenv('storage_account_name')
connection_string = os.getenv('connection_string')
container_name = os.getenv('container_name')


@app.get("/upload/", response_class=HTMLResponse, tags=["upload"])
async def upload_file(request: Request):
    return template.TemplateResponse("uploadPage.html", {"request": request})


@app.post("/upload/", tags=["upload"])
async def create_upload_file(description: str = Form(...),
                             keyword: str = Form(...),
                             file: UploadFile = File(...),
                             db: Session = Depends(get_db)):
    file_name = file.filename
    if crud.get_media_by_name(file_name, db):
        return f"Duplicate entry '{file_name}'"
    if not file:
        return {"message": "No upload file sent"}
    else:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        try:
            contents = file.file.read()
            file.file.seek(0)
            blob_client.upload_blob(contents)
            object_url = blob_client.url
        except Exception as e:
            logging.error(e)
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
    

async def create_media(media: Media, keyword: str, db: Session = Depends(get_db)):
    db_media = models.Media(**media.model_dump())
    db.add(db_media)
    db.commit()
    keyword = Keyword(keyword=keyword, owner_id=db_media.id)
    await create_media_keyword(keyword, db_media.id, db)
    
    
@app.patch("/media/{media_id}/description", tags=["media"])
async def change_media_description(media_id: int,
                                   description: str,
                                   db: Session = Depends(get_db)):
    return await crud.change_media_description(db=db, media_id=media_id, description=description)


@app.post("/media/{media_id}/keyword", tags=["media"])
async def create_media_keyword(keyword: Keyword,
                               media_id: int,
                               db: Session = Depends(get_db)):
    media = crud.get_media_by_id(db, media_id)
    if media:
        keyword = crud.create_media_keyword(db, keyword=keyword, owner_id=media_id)
        return keyword
    return f"{media_id} Does not exist"

@app.post("/media/search", tags=["media"])
def get_media_by_name(request: Request,
                      media_name: str | None = Form(None),
                      db: Session = Depends(get_db)):
    if media_name:
        medias = crud.get_media_by_name(db, media_name=media_name)
        image, video = [], []
        if medias:
            if medias[0].get('name').endswith(('.png', '.jpeg', '.jpg', '.gif')):
                image.append(medias[0])
            elif medias[0].get('name').endswith(('.mp4', '.webm', '.ogg')):
                video.append(medias[0])
        return template.TemplateResponse("displayPage.html", {"request": request, "images": image, "videos": video})
    return RedirectResponse("/medias/", 303)


@app.get("/media/", response_class=HTMLResponse, tags=["media"])
def read_medias(request: Request):
    medias = crud.get_media_record()
    image, video = [], []
    for media in medias:
        if media.get('name').endswith(('.png','.jpeg','.jpg','.gif')):
            image.append(media)
        elif media.get('name').endswith(('.mp4','.webm','.ogg')):
            video.append(media)
    return template.TemplateResponse("displayPage.html", {"request": request, "images": image, "videos": video})


@app.delete("/media/{media_id}", tags=["media"])
async def delete_media(media_id: int, db: Session = Depends(get_db)):
    media_name = crud.get_media_name(media_id, db)
    connector = BlobServiceClient.from_connection_string(connection_string)
    connector.get_blob_client(container_name, blob=media_name).delete_blob()
    return crud.delete_media(db=db, media_id=media_id)


@app.get("/login", tags=["login"], response_class=HTMLResponse)
async def login(request: Request):
    return template.TemplateResponse("loginPage.html", {"request": request})
   

@app.post("/login", tags=["login"])
async def login(username: str = Form(), password: str = Form()):
    credentials = {"username": username, "password": password}
    if check_credentials(credentials) == "Logged in!":
        return RedirectResponse("/upload", 303)
    return RedirectResponse("/login", 303)

def check_credentials(credentials: dict):
    return back_end.database.login(**credentials)


if __name__ == '__main__':
    uvicorn.run('app.main:app')
