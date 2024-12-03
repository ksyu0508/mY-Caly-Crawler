from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime
from app.database.models import Post, Information, Image  # Assuming models are in a file named models
from app.database.db import AsyncSessionLocal

router = APIRouter(prefix="/api/v1/query", tags=["query"])

@router.get("/posts/")
async def get_filtered_posts(
    startAt: Optional[datetime] = Query(None),
    endAt: Optional[datetime] = Query(None),
    type: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    college: Optional[str] = Query(None),
    search_term: Optional[str] = Query(None),
):
    async with AsyncSessionLocal() as db:
        # Query the database
        query = (
            select(Post)#, Information, Image)
            .options(joinedload(Post.information), joinedload(Post.image))
            .filter(Post.organized == True)
            .filter(Post.id == Image.post_id)
            .filter(Post.id == Information.post_id)
        )

        # Add filters for `Information` attributes
        if startAt:
            query = query.filter(Information.startAt >= startAt)
        if endAt:
            query = query.filter(Information.endAt <= endAt)
        if type:
            query = query.filter(Information.type == type)
        if tags:
            query = query.filter(Information.tags.overlap(tags))  # Check for overlapping tags
        if college:
            query = query.filter(Post.college == college)

        # Add filters for search term in `title`, `contents`, and `Image.img_contents`
        if search_term:
            search_filter = (
                Post.title.like(f"%{search_term}%")
                # | Post.contents.like(f"%{search_term}%")
                # | Image.img_contents.like(f"%{search_term}%")
            )
            query = query.filter(search_filter)

        result = await db.execute(query)
        posts = result.unique().scalars().all()

        # Format the response
        response = []

        for post in posts:
            response.append({
                "id": post.id,
                "title": post.title,
                "college": post.college,
                "link": post.original_link,
                "type": post.information[0].type if post.information else None,
                "tags": [info.tags for info in post.information],  # 모든 tags를 리스트로
                "contents": post.contents,
                "createdAt": post.createdAt,
                "startAt": post.information[0].startAt if post.information else None,
                "endAt": post.information[0].endAt if post.information else None,
                "images": [image.link for image in post.image],
            })

    return response