import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from blob_connector import BlobConnector
from azure.storage.blob import BlobServiceClient
from database_connector import MySQLConnector
from flask import Flask, request, redirect, render_template

app = FastAPI(description="Sample FastAPI App")

template = Jinja2Templates(directory="template")

@app.get("/")
async def root():
	return {"message": "Hello World"}
@app.get("/hello/{name}")
async def say_hello(name: str):
	return {"message": f"Hello {name}"}


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


@app.get('/mysql')
async def connect_mysql():
	mysql = MySQLConnector()
	mysql.connect()

if __name__ == '__main__':
	uvicorn.run('main:app')
