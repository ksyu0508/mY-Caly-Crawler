import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from typing import List, Dict

from app.crawlers.utils import *

async def crawl_urban_notice_board(url: str) -> List[Dict[str, str]]:
    """
    Crawl the notice board asynchronously and extract titles, links, and contents.
    """
    print(url)
    base_url = url.split('?')[0]
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, "html.parser")
        notices = []

        for item in soup.select("table.board-table tbody a"):
            link = item["href"]
            full_link = base_url + link
            result = await crawl_urban_article(session, full_link)
            notices.append(result)

            await asyncio.sleep(2)

        return notices

async def crawl_urban_article(session, url: str) -> Dict[str, str]:
    """
    Crawl an individual article page asynchronously.
    """
    print(f"Crawling article: {url}")
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")

    createdAt = "1999.01.01"
    title = soup.select_one('dl.board-write-box-v01 > dd').get_text(strip=True)
    createdAt = soup.select_one('dl.board-write-box-v02 > dd').get_text(strip=True).split('~')[0]
    createdAt = datetime.strptime(createdAt, "%Y.%m.%d")

    contents = []
    image_links = []

    base_img_url = "https://urban.yonsei.ac.kr"
    for item in soup.select("div.fr-view"):
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


async def get_urban(page_num: int = 1):
    notices = []
    for i in range(page_num):
        notices += await crawl_urban_notice_board("https://urban.yonsei.ac.kr/urban/notice/notice_under.do" + f'?mode=list&&articleLimit=10&article.offset={i * 10}')
        await asyncio.sleep(1)

    return notices


async def upsert_urban(page_num):
    posts = await get_urban(page_num=page_num)
    await upsert_posts(posts, college="도시공학과")


if __name__ == "__main__":
    notices = asyncio.run(upsert_urban(3))
    # for i, notice in enumerate(notices):
    #     print(f'#{i}:', notice)