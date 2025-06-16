import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import WordCloud from "wordcloud";
import NavBar from "../layouts/Navbar";
import Titleh2 from "../components/Titleh2";

// ✅ 新增 MUI 元件
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from "@mui/material";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const AlbumDetailPage = () => {
  const { id } = useParams();
  const [info, setInfo] = useState(null);
  const [emotions, setEmotions] = useState([]);
  const [topWords, setTopWords] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [lyricContent, setLyricContent] = useState("");
  const [lyricTitle, setLyricTitle] = useState("");

  const translateEmotionLabel = (label) => {
    switch (label) {
      case "positive":
        return "正向";
      case "negative":
        return "負向";
      case "neutral":
        return "中性";
      case "未知":
        return "未知";
      default:
        return label;
    }
  };

  const handleLyricClick = (lyricId) => {
    setShowModal(false); // ⛔ 先關掉，避免快速切換時 bug
    setLyricTitle("");
    setLyricContent("載入中...");

    fetch(`${API_BASE}/album/lyrics/${lyricId}`)
      .then((res) => res.json())
      .then((data) => {
        setLyricTitle(data.title);
        setLyricContent(data.lyrics || "（無歌詞）");
        setShowModal(true); // ✅ 確保是成功後才打開視窗
      })
      .catch(() => {
        setLyricTitle("讀取失敗");
        setLyricContent("無法載入歌詞，請稍後再試");
        setShowModal(true); // ⛔ 即使錯誤也顯示 Dialog 提示
      });
  };

  useEffect(() => {
    fetch(`${API_BASE}/album/album/${id}/info`)
      .then((res) => res.json())
      .then(setInfo);

    fetch(`${API_BASE}/album/${id}/emotions`)
      .then((res) => res.json())
      .then((data) => setEmotions(data.emotions || []));

    fetch(`${API_BASE}/album/${id}/top-words`)
      .then((res) => res.json())
      .then((data) => setTopWords(data.top_words || []));
  }, [id]);

  useEffect(() => {
    if (topWords.length > 0) {
      const canvas = document.getElementById("wordcloud");
      WordCloud(canvas, {
        list: topWords.slice(0, 100).map((w) => [w.word, w.count]),
        gridSize: 8,
        weightFactor: 10,
        fontFamily: "Arial",
        color: "random-dark",
        backgroundColor: "#fff",
      });
    }
  }, [topWords]);

  if (!info) return <p>載入中...</p>;

  return (
    <div className="album-detail-page">
      <NavBar />
      <div className="cover-img">
        {info.kkbox_cover && (
          <img
            src={JSON.parse(info.kkbox_cover)?.[2]?.url || ""}
            alt="kkbox cover"
          />
        )}
      </div>
      <h1>{info.album_name}</h1>
      <div className="album-info">
        <p>發行日期：{info.release_date}</p>
        <p>專輯類型：{info.album_type || "None"}</p>
        <Titleh2 title={"專輯介紹"} />
        <p className="description">{info.description}</p>
      </div>
      <div className="album-keyword">
        <div className="wordcloud-container">
          <Titleh2 title={"專輯文字雲"} />
          <canvas id="wordcloud" width="600" height="400"></canvas>
        </div>

        <div className="wordcloud-container">
          <Titleh2 title={"Top10 關鍵詞"} />
          <ul>
            {topWords.slice(0, 10).map((word, i) => (
              <li key={i}>
                {word.word} - {word.count}
              </li>
            ))}
          </ul>
        </div>
      </div>
      <Titleh2 title={"收錄歌曲"} />
      <div className="song-table">
        <table>
          <thead>
            <tr>
              <th>歌名</th>
              <th>情緒標籤</th>
              <th>情緒分數</th>
            </tr>
          </thead>
          <tbody>
            {emotions.map((song, idx) => (
              <tr key={idx}>
                <td>
                  <span
                    className="clickable-title"
                    onClick={() => handleLyricClick(String(song.lyric_id))}
                    style={{
                      color: "#007bff",
                      cursor: "pointer",
                      textDecoration: "underline",
                    }}
                  >
                    {song.title}
                  </span>
                </td>
                <td>{translateEmotionLabel(song.emotion_label)}</td>
                <td>{(song.emotion_score * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ✅ Material UI Dialog 彈出歌詞 */}
      <Dialog
        open={showModal}
        onClose={() => setShowModal(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{lyricTitle}</DialogTitle>
        <DialogContent dividers sx={{ maxHeight: "500px", overflowY: "auto" }}>
          {lyricContent.split("\n").map((line, idx) => (
            <Typography key={idx} variant="body1" paragraph>
              {line}
            </Typography>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowModal(false)} color="primary">
            關閉
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default AlbumDetailPage;
