import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export default function NewsList({ start, end, tag, keyword }) {
  const [news, setNews] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const params = new URLSearchParams();
        if (start) params.append("start", start);
        if (end) params.append("end", end);
        if (tag) params.append("tag", tag);
        if (keyword) params.append("keyword", keyword);

        const response = await fetch(`${API_BASE}/news/?${params}`);
        const data = await response.json();
        setNews(data);
      } catch (err) {
        console.error("新聞資料載入錯誤：", err);
        setError("無法載入新聞資料");
      }
    };

    fetchNews();
  }, [start, end, tag, keyword]);

  if (error) return <p>{error}</p>;
  if (!news.length) return <p>目前沒有新聞資料</p>;

  return (
    <div className="news-list">
      <ul>
        {news.map((item) => (
          <li key={item.id}>
            {item.image && (
              <img
                src={item.image}
                alt={item.title}
              />
            )}
            <a href={item.link} target="_blank" rel="noopener noreferrer">
              <h3>{item.title}</h3>
            <p>{item.date} | {item.tag}</p>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
