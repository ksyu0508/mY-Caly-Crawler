import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from typing import List, Dict

from app.crawlers.utils import *

async def crawl_ai_notice_board(url: str) -> List[Dict[str, str]]:
    """
    Crawl the notice board asynchronously and extract titles, links, and contents.
    """
    print(url)
    base_url = ""
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, "html.parser")
        notices = []

        for item in soup.select("div.basic_tbl_head.tbl_wrap table tbody div.bo_tit a"):
            link = item["href"]
            full_link = base_url + link
            result = await crawl_ai_article(session, full_link)
            notices.append(result)

            await asyncio.sleep(2)

        return notices

async def crawl_ai_article(session, url: str) -> Dict[str, str]:
    """
    Crawl an individual article page asynchronously.
    """
    print(f"Crawling article: {url}")
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")

    createdAt = "1999-01-01"
    title = soup.select_one('span.bo_v_tit').get_text(strip=True)
    createdAt = soup.select_one('strong.if_date').get_text(strip=True).replace('작성일', '').split(' ')[0]
    createdAt = datetime.strptime(createdAt, "%y-%m-%d")

    contents = []
    image_links = []

    base_img_url = ""
    for item in soup.find_all("div", {"id": "bo_v_con"}):
        content = item.get_text(strip=True)
        contents.append(content)
        
        img_tags = item.find_all("img")
        for img_tag in img_tags:
            if "src" in img_tag.attrs:
                image_links.append(base_img_url + img_tag["src"])

    contents = ''.join(contents)

    return {
        "title": title,
        "link": url,
        "contents": contents,
        "createdAt": createdAt,
        "image_links": image_links
    }


async def get_ai(page_num: int = 1):
    notices = []
    for i in range(page_num):
        notices += await crawl_ai_notice_board("https://ai.yonsei.ac.kr/bbs/board.php" + f'?bo_table=sub5_1&page={i+1}')
        await asyncio.sleep(1)

    return notices


async def upsert_ai(page_num):
    posts = await get_ai(page_num=page_num)
    await upsert_posts(posts, college="인공지능학과")


if __name__ == "__main__":
    notices = asyncio.run(upsert_ai(3))
    # for i, notice in enumerate(notices):
    #     print(f'#{i}:', notice)