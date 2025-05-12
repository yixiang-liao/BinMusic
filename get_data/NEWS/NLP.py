import requests
from bs4 import BeautifulSoup
import re
import os
import time
from datetime import datetime
import pandas as pd
import numpy
from collections import Counter
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker

csv_file = "binmusic_news.csv"

ws_driver = CkipWordSegmenter(model="albert-tiny")
pos_driver = CkipPosTagger(model="albert-tiny")
ner_driver = CkipNerChunker(model="albert-tiny")

df = pd.read_csv(csv_file)
all_names = df["Tag"].dropna().apply(lambda x: [name.strip() for name in str(x).split(",")])
name_list = list(set([name for sublist in all_names for name in sublist]))
name_list.sort()
# print(name_list)

# 自訂人名合併斷詞
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

# 主流程：讀取 CSV 並處理斷詞
def process_csv(filepath, text_column, custom_names):
    df = pd.read_csv(filepath)
    texts = df[text_column].fillna("").tolist()

    ws_result = ws_driver(texts)
    ws_result_merged = merge_custom_names(ws_result, custom_names, texts)

    pos_result = pos_driver(ws_result_merged)
    ner_result = ner_driver(ws_result)

    # 加入三個欄位
    df['ws_result'] = [' '.join(words) for words in ws_result_merged]
    df['pos_result'] = [' '.join(pos) for pos in pos_result]
    df['ner_result'] = [str([(e[0], e[1]) for e in ner]) for ner in ner_result]

    # 儲存到原始 CSV（覆寫）
    df.to_csv(filepath, index=False)

    return df


df = process_csv("binmusic_news.csv", "Content", name_list)