import React, { useEffect, useState } from "react";
import NavBar from "../layouts/NavBar";
import Titleh2 from "../components/Titleh2";
import NewsList from "../components/NewsList";
import WordCloud from "wordcloud";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const News = () => {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [tag, setTag] = useState("");
  const [keyword, setKeyword] = useState("");
  const [topWords, setTopWords] = useState([]);
  const [artists, setArtists] = useState([]);
  const [chartData, setChartData] = useState([]);

  // 取得所有藝人
  const fetchArtists = async () => {
    const res = await fetch(`${API_BASE}/artists`);
    const data = await res.json();
    setArtists(data);
  };

  const fetchWordCloud = async () => {
    const params = new URLSearchParams();
    if (start) params.append("start", start);
    if (end) params.append("end", end);
    if (tag) params.append("tag", tag);
    if (keyword) params.append("keyword", keyword);

    const res = await fetch(`${API_BASE}/news/wordcloud?${params}`);
    const data = await res.json();
    setTopWords(data.top_words || []);
  };

const fetchChartData = async () => {
  const params = new URLSearchParams();
  if (start) params.append("start", start);
  if (end) params.append("end", end);
  if (tag) params.append("tag", tag);
  if (keyword) params.append("keyword", keyword);

  const res = await fetch(`${API_BASE}/news/stats?${params}`);
  const data = await res.json();
  const rawCounts = data.counts || [];

  // 🔧 建立完整月份序列
  const getMonthList = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const months = [];

    start.setDate(1);
    while (start <= end) {
      const y = start.getFullYear();
      const m = (start.getMonth() + 1).toString().padStart(2, "0");
      months.push(`${y}-${m}`);
      start.setMonth(start.getMonth() + 1);
    }

    return months;
  };

  // 如果有指定日期則用指定範圍，否則取資料中最小與最大月份
  const allDates = rawCounts.map((item) => item.date);
  const first = start || (allDates.length ? allDates[0] : "2020-01");
  const last = end || (allDates.length ? allDates[allDates.length - 1] : "2020-12");

  const monthList = getMonthList(first, last);

  // 將資料轉成 Map 方便查詢
  const countMap = new Map(rawCounts.map((item) => [item.date, item.count]));

  // 補上沒有的月份
  const filledData = monthList.map((date) => ({
    date,
    count: countMap.get(date) || 0,
  }));

  setChartData(filledData);
};


  const handleCrawl = async () => {
    try {
      const res = await fetch(`${API_BASE}/news/crawl/news`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("爬取失敗");
      alert("✅ 成功爬取最新新聞！");
      fetchWordCloud();
      fetchChartData();
    } catch (err) {
      alert("❌ 爬取新聞失敗");
    }
  };

  const clearFilters = () => {
    setStart("");
    setEnd("");
    setTag("");
    setKeyword("");
  };

  useEffect(() => {
    fetchArtists();
  }, []);

  useEffect(() => {
    fetchWordCloud();
    fetchChartData();
  }, [start, end, tag, keyword]);

  useEffect(() => {
    if (topWords.length > 0) {
      const canvas = document.getElementById("wordcloud");
      WordCloud(canvas, {
        list: topWords.slice(0, 100).map((w) => [w.word, w.count]),
        gridSize: 8,
        weightFactor: (size) => Math.min(size * 2, 48),
        fontFamily: "Arial",
        color: "random-dark",
        backgroundColor: "#fff",
        rotateRatio: 0,
      });
    }
  }, [topWords]);

  return (
    <div className="news-page">
      <NavBar />
      <Titleh2 title="新聞專區" />

      {/* 篩選區 */}
      <div className="filter-section">
        <input
          type="date"
          value={start}
          onChange={(e) => setStart(e.target.value)}
        />
        <input
          type="date"
          value={end}
          onChange={(e) => setEnd(e.target.value)}
        />
        <select value={tag} onChange={(e) => setTag(e.target.value)}>
          <option value="">全部藝人</option>
          {artists.map((artist) => (
            <option key={artist.id} value={artist.name}>
              {artist.name}
            </option>
          ))}
        </select>
        <input
          type="text"
          placeholder="關鍵字"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
        />
        <button onClick={clearFilters}>清除欄位</button>
        <button onClick={handleCrawl}>爬取最新新聞</button>
      </div>

      {/* 折線圖 */}
      <div className="news-trend">
        <Titleh2 title="每日新聞數量折線圖" />
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="count"
                stroke="rgb(156, 198, 21)"
                fill="rgb(156, 198, 21)"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 文字雲 + Top 關鍵詞 */}
      <div className="wordcloud-keywords">
        <div className="wordcloud-wrapper">
          <Titleh2 title="新聞文字雲" />
          <canvas id="wordcloud" width="1000" height="500"></canvas>
        </div>

        <div className="top-keywords">
          <Titleh2 title="Top 15 關鍵詞" />
          <ul>
            {topWords.slice(0, 15).map((item, i) => (
              <li key={i}>
                {item.word} - {item.count}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 新聞列表 */}
      <Titleh2 title="新聞列表" />
      <NewsList start={start} end={end} tag={tag} keyword={keyword} />
    </div>
  );
};

export default News;
