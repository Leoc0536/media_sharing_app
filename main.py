from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

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

if __name__ == '__main__':
	uvicorn.run('main:app')