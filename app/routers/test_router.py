from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.ocr import perform_ocr
from app.document import perform_llm, process_posts
from app.crawlers.common_crawler import upsert_common

from pydantic import HttpUrl

router = APIRouter(prefix="/api/v1/debug", tags=["Endpoint For Debugging"])

@router.get("/ocr")
async def get_ocr(target_url: HttpUrl = Query(..., description="The target URL")):
    contents = await perform_ocr(str(target_url))
    return {"contents": contents}


@router.get("/llm")
async def get_llm(target_content: str = Query(..., description="target contents")):
    contents = await perform_llm(str(target_content))
    return {"contents": contents}


@router.post("/crawl/common")
async def crawl_common():
    try:
        await upsert_common()
        return {"message": "Success"}
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}


@router.post("/organize")
async def post_organize():
    try:
        await process_posts()
        return {"message": "Success"}
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}


