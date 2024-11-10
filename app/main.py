# app/main.py
from fastapi import FastAPI
from app.routers import example_router

app = FastAPI()

app.include_router(example_router.router)

@app.get("/")
def read_root():
    return {"message": "mY-Caly-Crawler Opened"}
