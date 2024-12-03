import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from typing import List, Dict

from app.crawlers.utils import *
# from sqlalchemy.future import select, update


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
                # title = a_tag.get_text(strip=True)
                link = a_tag["href"]
                full_link = base_url + link

                # Crawl the article with a delay
                result = await crawl_common_article(session, full_link)
                notices.append(result)

                # Add delay between requests
                await asyncio.sleep(2)  # Delay for 2 seconds between requests

        return notices

async def crawl_common_article(session, url: str) -> Dict[str, str]:
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

        strong_tag = item.find("strong")
        title = strong_tag.get_text(strip=True)

    contents = []
    image_links = []

    base_img_url = "https://www.yonsei.ac.kr"
    for item in soup.select("div.cont_area"):
        p_tag = item.find("p")
        if not p_tag:
            continue
        content = p_tag.get_text(strip=True)
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


async def get_common(page_num: int = 1):
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
    posts = await get_common(page_num=3)
    await upsert_posts(posts, college="common")


# if __name__ == "__main__":
#     asyncio.run(upsert_common())
