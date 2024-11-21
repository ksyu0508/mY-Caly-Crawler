import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def crawl_notice_board(url: str) -> List[Dict[str, str]]:
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    notices = []
    
    # 예시: 공지사항이 'li' 태그 안에 있는 경우
    for item in soup.select("ul.board_list > li"):
        a_tag = item.find("a")
        if a_tag:
            title = a_tag.get_text(strip=True)
            link = a_tag["href"]

            contents = crawl_article(url+link)
            
            notices.append({
                "title": title,
                "link": link,
                "contents": contents,
            })
    
    return notices

def crawl_article(url):
    print(url)
    response = requests.get(url)
    response.raise_for_status()  # 요청 실패 시 에러 발생

    soup = BeautifulSoup(response.text, "html.parser")

    contents = []    
    for item in soup.select("dl.board_view > dd"):
        p_tag = item.find("p")
        if p_tag:
            content = p_tag.get_text(strip=True)
            contents.append(content)
    contents = ''.join(contents)

    return contents

if __name__ == '__main__':
    url = "https://www.yonsei.ac.kr/sc/support/notice.jsp"
    notices = crawl_notice_board(url)

    for notice in notices:
        print(f"Title: {notice['title']}, Link: {notice['link']}, Contents: {notice['contents']}")