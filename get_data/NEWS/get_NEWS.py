import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import pandas as pd
from datetime import datetime


base_url = "https://www.bin-music.com.tw/news"
user_agent = UserAgent()

title_list = []
date_list = []
link_list = []
img_list = []
item_id = []
content_list = []
tag_list = []


# 模擬瀏覽器抓首頁以找頁數
req = requests.get(base_url, headers={ 'user-agent': user_agent.random }, timeout=5)
soup = BeautifulSoup(req.text, 'lxml')
pages = soup.find('li', {'class': "info"}).text
pages = int(pages[-3:])

# 抓全部頁面
for page in range(1, pages + 1):
    page_url = f"{base_url}/p{page}"
    res = requests.get(page_url, headers={ 'user-agent': user_agent.random }, timeout=5)
    soup_page = BeautifulSoup(res.text, 'lxml')
    content_blocks = soup_page.find_all('div', {'class': "two-col"})
    print(f"Page {page}: {len(content_blocks)} items")

    for block in content_blocks:
        title = block.find('div', class_='title').text.strip()
        date = block.find('div', class_='date').text.strip()
        date_obj = datetime.strptime(date, "%Y.%m.%d")
        link = block.find('a')['href']
        full_link = f"https://www.bin-music.com.tw{link}" if link.startswith('/') else link

        content_page = requests.get(full_link, headers={ 'user-agent': user_agent.random }, timeout=5)
        content_soup = BeautifulSoup(content_page.text, 'lxml')
        img = content_soup.find('img' , class_='mobile')['src']
        content_p = content_soup.find_all('p')
        content = ''
        for i in content_p:
            content += i.text.strip()

        tag_div = content_soup.find('div', class_='tag')
        if tag_div:
            tags = [a.text.strip() for a in tag_div.find_all('a')]
            tag_string = ','.join(tags)
        else:
            tag_string = ''

        tag_list.append(tag_string)
        content_list.append(content)
        title_list.append(title)
        date_list.append(date_obj.strftime("%Y-%m-%d"))
        link_list.append(full_link)
        img_list.append(img)
        item_id.append(full_link[-4:])
        print(f'{date_obj.strftime("%Y-%m-%d")} - {tag_string} - {title}')

    time.sleep(1)

# 匯出為 CSV
df = pd.DataFrame({
    'ID': item_id,
    'Tag': tag_list,
    'Title': title_list,
    'Date': date_list,
    'Link': link_list,
    'Image': img_list,
    'Content': content_list
})

df.to_csv('binmusic_news.csv', index=False, encoding='utf-8-sig')
print("✅ 匯出完成：binmusic_news.csv")
