# app/main.py
from fastapi import FastAPI
from app.routers import crawling_router
from app.config import Config

app = FastAPI(
    title=Config.TITLE,
    
)

app.include_router(crawling_router.router)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "mY-Caly-Crawler Opened"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )