import { useParams } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import WordCloud from "wordcloud";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import NavBar from "../layouts/Navbar";
import AlbumList from "../components/AlbumList";
import { parse, format, addMonths, isBefore } from "date-fns";
import Footer from "../layouts/Footer";

export default function ArtistDetailPage() {
  const { id } = useParams();
  const API_BASE = import.meta.env.VITE_API_BASE_URL;
  const [artist, setArtist] = useState(null);
  const [stats, setStats] = useState(null);
  const [yearData, setYearData] = useState(null);
  const [albums, setAlbums] = useState([]);
  const canvasRef = useRef(null);
  const [newsVolume, setNewsVolume] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/artists`)
      .then((res) => res.json())
      .then((data) => setArtist(data.find((a) => a.id === Number(id))));

    fetch(`${API_BASE}/artist-stats/${id}`)
      .then((res) => res.json())
      .then(setStats);

    fetch(`${API_BASE}/${id}/albums/yearly`)
      .then((res) => res.json())
      .then(setYearData);

    fetch(`${API_BASE}/artists/${id}/albums/with-kkbox`)
      .then((res) => res.json())
      .then(setAlbums);

    fetch(`${API_BASE}/news/artist-volume/${id}`)
      .then((res) => res.json())
      .then(setNewsVolume);
  }, [id]);

  const top100Words = Array.isArray(stats?.top_words)
    ? stats.top_words
        .filter((w) => w.word && w.count)
        .sort((a, b) => b.count - a.count)
        .slice(0, 300)
    : [];

  const wordCloudWords = top100Words.map(({ word, count }) => ({
    text: word || "詞",
    value: count || 1,
  }));

  useEffect(() => {
    if (!canvasRef.current || wordCloudWords.length === 0) return;

    const list = wordCloudWords.map(({ text, value }) => [text, value]);

    WordCloud(canvasRef.current, {
      list,
      fontFamily: "Noto Sans TC",
      gridSize: 8,
      weightFactor: (size) => Math.log2(size + 1) * 8,
      rotateRatio: 0.3,
      rotationSteps: 2,
      backgroundColor: "#fff",
      color: () => {
        const colors = [
          "#1abc9c",
          "#3498db",
          "#9b59b6",
          "#e74c3c",
          "#e67e22",
          "#f39c12",
          "#2ecc71",
          "#34495e",
        ];
        return colors[Math.floor(Math.random() * colors.length)];
      },
      drawOutOfBound: false,
      origin: [250, 150],
      shuffle: true,
      shape: "circle",
      ellipticity: 1,
    });
  }, [wordCloudWords]);

  if (!artist || !stats || !yearData) return <p>Loading...</p>;

  const top10Words = top100Words.slice(0, 15);

const fillMissingYears = (yearCounts) => {
  const years = Object.keys(yearCounts)
    .map((y) => parseInt(y))
    .filter((y) => !isNaN(y))
    .sort((a, b) => a - b);

  if (years.length === 0) return [];

  const start = years[0];
  const end = years[years.length - 1];
  const result = [];

  for (let y = start; y <= end; y++) {
    result.push({
      year: String(y),
      count: yearCounts[String(y)] || 0,
    });
  }

  return result;
};
  const chartData = fillMissingYears(yearData.year_counts);

    // 🔁 補滿每個月
const fillMissingMonths = (dataMap) => {
  const keys = Object.keys(dataMap).sort();
  if (keys.length === 0) return [];

  const start = parse(keys[0], "yyyy-MM", new Date());
  const end = parse(keys[keys.length - 1], "yyyy-MM", new Date());
  const result = [];

  let current = start;
  while (isBefore(current, addMonths(end, 1))) {
    const key = format(current, "yyyy-MM");
    result.push({
      month: key,
      count: dataMap[key] || 0,
    });
    current = addMonths(current, 1);
  }

  return result;
};


  const newsChartData =
  newsVolume.length > 0
    ? fillMissingMonths(newsVolume[0].data)
    : [];

  return (
    <div className="artist-detail-page">
      <NavBar />
      <div className="containerB">
        <div
          className="artist-hero"
          style={{ backgroundImage: `url(${artist.bin_img})` }}
        >
          <div className="overlay"></div>
          <div className="artist-text">
            <h1>{artist.name}</h1>
            <h2>{artist.en_name}</h2>
            <p>
              {Array.isArray(artist.genres)
                ? artist.genres.join(" / ")
                : JSON.parse(artist.genres || "[]").join(" / ")}
            </p>
          </div>
        </div>

        <p className="intro">{artist.bin_intro}</p>

        <h2>專輯列表</h2>
        <AlbumList api={`${API_BASE}/artists/${id}/albums/with-kkbox`} />

        <h2>年份作品統計</h2>
        <div className="chart" style={{ width: "80%", height: 300 }}>
          <ResponsiveContainer>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <h2>新聞曝光趨勢</h2>
        <div className="chart" style={{ width: "80%", height: 300 }}>
          <ResponsiveContainer>
            <AreaChart data={newsChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="keyword">
          <div>
            <h2>Top 歌詞文字雲</h2>
            <canvas
              ref={canvasRef}
              width={1000}
              height={600}
              style={{
                //   display: "block",
                margin: "0 auto",
                //   border: "1px solid #ccc",
                //   borderRadius: "8px",
                background: "#fff",
                maxWidth: "100%", // 外觀可縮放，但畫布內解析度固定
              }}
            ></canvas>
          </div>
          <div>
            <h2>Top 10 歌詞詞彙統計</h2>
            <ul>
              {top10Words.map((w) => (
                <li key={w.word}>
                  {w.word}（{w.count} 次）
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
