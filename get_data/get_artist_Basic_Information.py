import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
from fake_useragent import UserAgent
from db.model.artists import Artist
from db.base import Base, SessionLocal, engine

user_agent = UserAgent()
user_agent.random

Base.metadata.create_all(bind=engine)
session = SessionLocal()

url = 'https://www.bin-music.com.tw/artist'
req = requests.get(url, headers={ 'user-agent': user_agent.random }, timeout=5)

page = BeautifulSoup(req.text,'lxml')
# print(page.prettify())

content = page.findAll('div', {'class':"artist-box"})

artist_type = {'告五人':'band' , '宇宙人':'band' , '五月天':'band' , '麋先生':'band', 'Tizzy Bac':'band', 'Energy':'group'}

for div in content:
    link_tag = div.find('a')
    href = link_tag['href'] if link_tag else ''
    
    title_div = div.find('div', class_='title')
    zh_name = title_div.contents[0].strip() if title_div else ''
    en_name = title_div.find('span').text.strip() if title_div and title_div.find('span') else ''

    req_info = requests.get(href, headers={ 'user-agent': user_agent.random }, timeout=5)
    page_info = BeautifulSoup(req_info.text,'lxml')
    intro = page_info.find('div', {'class':"content"})
    intro = intro.text.strip().replace('\r', '').replace('\n\n\n', '\n').replace('\n\n', '\n') if intro else ''
    if zh_name in artist_type:
        type = artist_type[zh_name]
    else:
        type = 'solo'

    print(f'zh_name: {zh_name}')
    print(f'en_name: {en_name}')
    print(f'href: {href}')
    print(f'intro: {intro}')
    print(f'type: {type}')
    print('---')

    artist = Artist(name=zh_name, en_name=en_name, bin_url=href, bin_intro=intro , type=type)
    session.add(artist)

    session.commit()
    
    print(f'完成儲存{zh_name}的資料')
