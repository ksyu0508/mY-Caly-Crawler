from typing import List, Dict

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update

from app.ocr import perform_ocr
from app.database.models import Post, Image
from app.database.db import AsyncSessionLocal

async def fetch(session, url: str) -> str:
    """
    Fetch the content of the given URL asynchronously.
    """
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def upsert_posts(data: List[Dict], college: str='common'):
    """
    Asynchronously insert or update posts and associated images in the database.
    Args:
        data (List[Dict]): List of dictionaries containing post data.
        college (str): College name to associate with the post.
    """
    async with AsyncSessionLocal() as db:
        for entry in data:
            # Extract relevant fields
            title = entry["title"]
            link = entry["link"]
            contents = entry["contents"]
            image_links = entry["image_links"]
            createdAt = entry["createdAt"]

            # Check if the post already exists by title
            q = select(Post).filter(Post.title == title)
            existing_post = await db.execute(q)
            existing_post = existing_post.scalar_one_or_none()

            if existing_post:
                # db.execute(
                #      update(Post).
                #      where(Post.id == existing_post.id).
                #      values(contents=contents)
                #  )
                continue
            else:
                new_post = Post(
                    title=title,
                    contents=contents,
                    college=college,
                    original_link=link,
                    createdAt=createdAt,
                    organized=False  # Default value
                )
                # Add the post to the session
                db.add(new_post)
                await db.flush()  # Flush to get the new post ID

            # Add associated images
            for image_link in image_links:
                img_contents = await perform_ocr(image_url=image_link)
                
                # q = select(Image).filter(Image.link == image_link)
                # existing_img = await db.execute(q)
                # existing_img = existing_img.scalar_one_or_none()
                
                # if existing_img:
                #     db.execute(
                #         update(Image).
                #         where(Image.link == image_link).
                #         values(img_contents=img_contents)
                #     )
                #     continue

                new_image = Image(post_id=new_post.id, link=image_link, img_contents=img_contents)
                db.add(new_image)

        try:
            await db.commit()
            print("All data committed successfully!")
        except IntegrityError as e:
            await db.rollback()
            print(f"Database error: {e}")
