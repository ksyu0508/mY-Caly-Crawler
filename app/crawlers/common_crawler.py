import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from typing import List, Dict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

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

async def crawl_common_notice_board(url: str) -> List[Dict[str, str]]:
    """
    Crawl the notice board asynchronously and extract titles, links, and contents.
    """
    base_url = url.split('?')[0]
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, "html.parser")
        notices = []

        # Process all notice items
        for item in soup.select("ul.board_list > li"):
            a_tag = item.find("a")
            if a_tag:
                title = a_tag.get_text(strip=True)
                link = a_tag["href"]
                full_link = base_url + link

                # Crawl the article with a delay
                result = await crawl_common_article(session, full_link, title)
                notices.append(result)

                # Add delay between requests
                await asyncio.sleep(2)  # Delay for 2 seconds between requests

        return notices

async def crawl_common_article(session, url: str, title: str) -> Dict[str, str]:
    """
    Crawl an individual article page asynchronously.
    """
    print(f"Crawling article: {url}")
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")

    createdAt = "1999.01.01"
    for item in soup.select("dl.board_view > dt"):
        p_tag = item.find("span")
        content = p_tag.get_text(strip=True).split('~')[0]
        createdAt = datetime.strptime(content, "%Y.%m.%d")

    contents = []
    image_links = []

    base_img_url = "https://www.yonsei.ac.kr"
    for item in soup.select("div.cont_area"):
        p_tag = item.find("p")
        if not p_tag:
            continue
        content = p_tag.get_text(strip=True)
        contents.append(content)
        
        img_tag = item.find("img")
        if img_tag and "src" in img_tag.attrs:
            image_links.append(base_img_url + img_tag["src"])
    
    contents = ''.join(contents)

    return {
        "title": title,
        "link": url,
        "contents": contents,
        "createdAt": createdAt,
        "image_links": image_links
    }


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
                continue
            
            for image_link in image_links:
                contents += await perform_ocr(image_url=image_link)

            # Create a new Post object
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
                new_image = Image(post_id=new_post.id, link=image_link)
                db.add(new_image)

        try:
            await db.commit()
            print("All data committed successfully!")
        except IntegrityError as e:
            await db.rollback()
            print(f"Database error: {e}")


async def get_common(page_num: int = 5):
    notices = []
    for i in range(page_num):
        notices += await crawl_common_notice_board("https://www.yonsei.ac.kr/sc/support/notice.jsp" + f'?mode=list&pager.offset={10 * i}')
        await asyncio.sleep(1)
    for i in range(page_num):
        notices += await crawl_common_notice_board("https://www.yonsei.ac.kr/sc/support/etc_notice.jsp" + f'?mode=list&pager.offset={10 * i}')
        await asyncio.sleep(1)
    for i in range(page_num):
        notices += await crawl_common_notice_board("https://www.yonsei.ac.kr/sc/support/scholarship.jsp" + f'?mode=list&pager.offset={10 * i}')
        await asyncio.sleep(1)

    return notices
    # for i, notice in enumerate(notices):
    #     print(f'#{i}', notice)


async def upsert_common():
    posts = await get_common(page_num=5)
    await upsert_posts(posts, college="common")


# if __name__ == "__main__":
#     asyncio.run(upsert_common())
