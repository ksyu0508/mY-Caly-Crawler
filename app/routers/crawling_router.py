# app/routers/example_router.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.crawler import crawl_notice_board

router = APIRouter()

class URLItem(BaseModel):
    url: str = None

@router.get("/notice/{url}")
async def create_item(url: str):
    contents = crawl_notice_board(url)
    return {"contents": contents}
