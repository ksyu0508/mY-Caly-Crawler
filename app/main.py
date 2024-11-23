# app/main.py
from fastapi import FastAPI
from app.routers import crawling_router, test_router

from app.config import Config
from app.database.db import engine, sync_engine
from app.database.models import Post, Information, Image

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

app = FastAPI(title=Config.TITLE)
scheduler = BackgroundScheduler()

# app.include_router(crawling_router.router)
app.include_router(test_router.router)

def sample_task():
    print("This task runs on a schedule!")

scheduler.add_job(sample_task, CronTrigger(hour="*/1"))

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:  # Use async_engine for async operations
        await conn.run_sync(Post.metadata.create_all)
        await conn.run_sync(Image.metadata.create_all)
        await conn.run_sync(Information.metadata.create_all)
    # Image.metadata.create_all(bind=sync_engine)
    # Post.metadata.create_all(bind=sync_engine)
    # Information.metadata.create_all(bind=sync_engine)
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

@app.get("/")
def read_root():
    return {"message": "mY-Caly-Crawler Opened"}
