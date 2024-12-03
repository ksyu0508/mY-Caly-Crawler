import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from typing import List, Dict

from app.crawlers.utils import *

async def crawl_arch_notice_board(url: str) -> List[Dict[str, str]]:
    """
    Crawl the notice board asynchronously and extract titles, links, and contents.
    """
    print(url)
    base_url = "https://arch.yonsei.ac.kr"
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, "html.parser")
        notices = []

        rows = soup.select("table.board-list tbody tr")
        for row in rows:
            link_tag = row.find("td", class_="title").find("a")
            if link_tag:
                link = link_tag["href"]
                full_link = base_url + link

            # Extract the date
            date_tag = row.find("td", class_="packed hide-on-small-only").find("a")
            if date_tag:
                createdAt = date_tag.get_text(strip=True)
                createdAt = datetime.strptime(createdAt, "%Y-%m-%d")

            result = await crawl_arch_article(session, full_link, createdAt)

            notices.append(result)

            await asyncio.sleep(2)

        return notices

async def crawl_arch_article(session, url: str, createdAt) -> Dict[str, str]:
    """
    Crawl an individual article page asynchronously.
    """
    print(f"Crawling article: {url}")
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")

    # createdAt = "1999.01.01"
    title = soup.select_one('div.dcore-body').get_text(strip=True)
    # createdAt = soup.select_one('dl.board-write-box-v02 > dd').get_text(strip=True).split('~')[0]
    # createdAt = datetime.strptime(createdAt, "%Y.%m.%d")

    contents = []
    image_links = []

    base_img_url = "https://arch.yonsei.ac.kr"
    for item in soup.select("div.post-body"):
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


async def get_arch(page_num: int = 1):
    notices = []
    for i in range(page_num):
        notices += await crawl_arch_notice_board("https://arch.yonsei.ac.kr/notice/" + f'page/{i+1}')
        await asyncio.sleep(1)

    return notices


async def upsert_arch(page_num):
    posts = await get_arch(page_num=page_num)
    await upsert_posts(posts, college="도시공학과")


if __name__ == "__main__":
    notices = asyncio.run(upsert_arch(3))
    # for i, notice in enumerate(notices):
    #     print(f'#{i}:', notice)