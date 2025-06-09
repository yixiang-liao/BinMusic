import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import pandas as pd
from datetime import datetime
import os
import re
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker

# CKIP 初始化
ws_driver = CkipWordSegmenter(model="albert-tiny")
pos_driver = CkipPosTagger(model="albert-tiny")
ner_driver = CkipNerChunker(model="albert-tiny")

base_url = "https://www.bin-music.com.tw/news"
user_agent = UserAgent()
csv_file = "binmusic_news.csv"

# 已存在 ID 判斷
def get_existing_ids(filepath):
    if not os.path.exists(filepath):
        return set()
    df = pd.read_csv(filepath)
    return set(df["ID"].astype(str))

# 自訂人名斷詞合併
def merge_custom_names(ws_results, custom_names, original_sentences):
    merged_results = []
    for tokens, raw_text in zip(ws_results, original_sentences):
        spans = []
        for name in custom_names:
            for match in re.finditer(re.escape(name), raw_text):
                spans.append((match.start(), match.end(), name))
        spans.sort()
        filtered_spans = []
        last_end = -1
        for start, end, name in spans:
            if start >= last_end:
                filtered_spans.append((start, end, name))
                last_end = end
        merged = []
        idx = 0
        char_idx = 0
        for start, end, name in filtered_spans:
            while idx < len(tokens) and char_idx + len(tokens[idx]) <= start:
                merged.append(tokens[idx])
                char_idx += len(tokens[idx])
                idx += 1
            merged.append(name)
            skip_len = end - start
            temp_len = 0
            while idx < len(tokens) and temp_len < skip_len:
                temp_len += len(tokens[idx])
                char_idx += len(tokens[idx])
                idx += 1
        merged.extend(tokens[idx:])
        merged_results.append(merged)
    return merged_results

# NLP 分析
def process_nlp(df, custom_names):
    texts = df["Content"].fillna("").tolist()
    ws_result = ws_driver(texts)
    ws_result_merged = merge_custom_names(ws_result, custom_names, texts)
    pos_result = pos_driver(ws_result_merged)
    ner_result = ner_driver(ws_result)

    df["ws_result"] = [" ".join(words) for words in ws_result_merged]
    df["pos_result"] = [" ".join(tags) for tags in pos_result]
    df["ner_result"] = [str([(e[0], e[1]) for e in chunk]) for chunk in ner_result]
    return df

# --- 主程式 ---
title_list, date_list, link_list, img_list = [], [], [], []
item_id, content_list, tag_list = [], [], []

existing_ids = get_existing_ids(csv_file)

# 模擬瀏覽器抓首頁以找頁數
req = requests.get(base_url, headers={ 'user-agent': user_agent.random }, timeout=5)
soup = BeautifulSoup(req.text, 'lxml')
pages = soup.find('li', {'class': "info"}).text
pages = int(pages[-3:])

print(f"📄 共有 {pages} 頁新聞，已存在 {len(existing_ids)} 筆")

for page in range(1, pages + 1):
    page_url = f"{base_url}/p{page}"
    res = requests.get(page_url, headers={ 'user-agent': user_agent.random }, timeout=5)
    soup_page = BeautifulSoup(res.text, 'lxml')
    content_blocks = soup_page.find_all('div', {'class': "two-col"})
    print(f"📥 Page {page}: {len(content_blocks)} items")

    for block in content_blocks:
        title = block.find('div', class_='title').text.strip()
        date = block.find('div', class_='date').text.strip()
        date_obj = datetime.strptime(date, "%Y.%m.%d")
        link = block.find('a')['href']
        full_link = f"https://www.bin-music.com.tw{link}" if link.startswith('/') else link
        news_id = full_link[-4:]

        if news_id in existing_ids:
            continue  # 已存在的新聞略過

        content_page = requests.get(full_link, headers={ 'user-agent': user_agent.random }, timeout=5)
        content_soup = BeautifulSoup(content_page.text, 'lxml')
        img = content_soup.find('img', class_='mobile')['src']
        content_p = content_soup.find_all('p')
        content = ''.join(p.text.strip() for p in content_p)

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
        item_id.append(news_id)
        print(f"✅ 新增：{date_obj.strftime('%Y-%m-%d')} - {title} - {tag_string}")

    time.sleep(1)

# 新資料儲存與 NLP
if not item_id:
    print("✅ 無新新聞需要更新。")
else:
    df_new = pd.DataFrame({
        'ID': item_id,
        'Tag': tag_list,
        'Title': title_list,
        'Date': date_list,
        'Link': link_list,
        'Image': img_list,
        'Content': content_list
    })

    # 建立人名清單
    if os.path.exists(csv_file):
        df_old = pd.read_csv(csv_file)
        all_names = df_old["Tag"].dropna().apply(lambda x: [name.strip() for name in str(x).split(",")])
        name_list = sorted(set(name for sublist in all_names for name in sublist))
    else:
        df_old = pd.DataFrame()
        name_list = []

    df_new = process_nlp(df_new, name_list)

    df_all = pd.concat([df_old, df_new], ignore_index=True)
    df_all["ID"] = df_all["ID"].astype(int)
    df_all = df_all.sort_values(by="ID", ascending=False)
    df_all.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"📦 共新增 {len(df_new)} 筆，已儲存至 {csv_file}")
