from fastapi import APIRouter
from pydantic import BaseModel
from app.crawlers.common_crawler import crawl_common_notice_board

# router = APIRouter()

# class URLItem(BaseModel):
#     url: str = None

# @router.post("/notice")
# async def create_item(url: URLItem):
#     contents = crawl_notice_board(url.url)
#     return {"contents": contents}
