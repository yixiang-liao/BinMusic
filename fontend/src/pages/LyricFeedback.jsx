import React, { useState, useEffect } from "react";
import NavBar from "../layouts/NavBar";
import Titleh2 from "../components/Titleh2";
import axios from "axios";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Checkbox,
  FormControlLabel,
  Typography,
} from "@mui/material";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const feelingOptions = [
  "感動",
  "療癒",
  "熱血",
  "悲傷",
  "平靜",
  "孤單",
  "鼓舞",
  "回憶湧現",
  "想起某個人",
  "想哭",
  "想跳舞",
  "想戀愛",
];

const LyricFeedback = () => {
  const [artists, setArtists] = useState([]);
  const [selectedArtistId, setSelectedArtistId] = useState("");
  const [searchKeyword, setSearchKeyword] = useState("");
  const [songs, setSongs] = useState([]);
  const [filteredSongs, setFilteredSongs] = useState([]);
  const [selectedSong, setSelectedSong] = useState(null);
  const [lyrics, setLyrics] = useState([]);
  const [selectedLines, setSelectedLines] = useState([]);
  const [feelings, setFeelings] = useState([]);
  const [reason, setReason] = useState("");
  const [userName, setUserName] = useState("");
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    axios.get(`${API_BASE}/album/lyrics/all`).then((res) => {
      setSongs(res.data);
      setFilteredSongs(res.data);
    });
    axios.get(`${API_BASE}/artists`).then((res) => setArtists(res.data));
  }, []);

  useEffect(() => {
    const keyword = searchKeyword.toLowerCase();
    const filtered = songs.filter((s) => {
      const matchArtist = selectedArtistId
        ? String(s.artist_id) === String(selectedArtistId)
        : true;
      const matchKeyword =
        s.title.toLowerCase().includes(keyword) ||
        s.artist_name.toLowerCase().includes(keyword) ||
        s.album_name.toLowerCase().includes(keyword);
      return matchArtist && matchKeyword;
    });
    setFilteredSongs(filtered);
  }, [searchKeyword, songs, selectedArtistId]);

  const openLyricsModal = (song) => {
    setSelectedSong(song);
    axios
      .get(`${API_BASE}/lyric_feedback/lyrics/${song.lyric_id}/lines`)
      .then((res) => {
        setLyrics(res.data);
        setSelectedLines([]);
        setFeelings([]);
        setReason("");
        setUserName("");
        setShowModal(true);
      });
  };

  const handleSubmit = () => {
    axios
      .post(`${API_BASE}/lyric_feedback/`, {
        lyric_id: selectedSong.lyric_id,
        selected_lines: selectedLines,
        feeling: feelings,
        reason,
        user_name: userName || "匿名",
      })
      .then(() => setShowModal(false));
  };

  const handleLineClick = (lineNumber) => {
    if (
      selectedLines.length === 0 ||
      Math.abs(lineNumber - selectedLines[0]) >= 5
    ) {
      setSelectedLines([lineNumber]);
    } else {
      const min = Math.min(selectedLines[0], lineNumber);
      const max = Math.max(selectedLines[0], lineNumber);
      const rangeLength = max - min + 1;
      if (rangeLength <= 5) {
        const range = Array.from({ length: rangeLength }, (_, i) => min + i);
        setSelectedLines(range);
      } else {
        setSelectedLines([lineNumber]);
      }
    }
  };

  const parseCoverUrl = (coverJson) => {
    try {
      const parsed = JSON.parse(coverJson);
      return parsed.find((img) => img.width === 160)?.url || "";
    } catch {
      return "";
    }
  };

  return (
    <div className="lyric-feedback-page">
      <NavBar />
      <div className="cont">
        <Titleh2 title="歌詞互動" />

        <div className="filter-bar">
          <select
            value={selectedArtistId}
            onChange={(e) => setSelectedArtistId(e.target.value)}
          >
            <option value="">全部藝人</option>
            {artists.map((artist) => (
              <option key={artist.id} value={artist.id}>
                {artist.name}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="搜尋歌曲、專輯"
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
          />
          <button
            onClick={() => {
              setSearchKeyword("");
              setSelectedArtistId("");
            }}
          >
            清除
          </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>封面</th>
              <th>歌曲</th>
              <th>所屬專輯</th>
              <th>藝人</th>
            </tr>
          </thead>
          <tbody>
            {filteredSongs.map((song) => (
              <tr key={song.lyric_id} onClick={() => openLyricsModal(song)}>
                <td className="cover">
                  <img
                    src={parseCoverUrl(song.kkbox_cover)}
                    width="60"
                    height="60"
                  />
                </td>
                <td>{song.title}</td>
                <td>{song.album_name}</td>
                <td>{song.artist_name}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <Dialog
          open={showModal}
          onClose={() => setShowModal(false)}
          fullWidth
          maxWidth="md"
        >
          <DialogTitle>
            <Typography variant="h6">
              {selectedSong?.title} - {selectedSong?.artist_name}
            </Typography>
          </DialogTitle>
          <DialogContent>
            <div className="lyrics-container">
              <hr />
              <label>選取1~5行歌詞</label>
              <Button
                onClick={() => setSelectedLines([])}
                style={{ float: "right", marginBottom: "10px" }}
              >
                清除選取
              </Button>
              {lyrics.map((line, idx) => (
                <p
                  key={idx}
                  onClick={() => handleLineClick(line.line_number)}
                  style={{
                    cursor: "pointer",
                    backgroundColor: selectedLines.includes(line.line_number)
                      ? "#d0f0fd"
                      : "transparent",
                  }}
                >
                  {line.text}
                </p>
              ))}
            </div>
            <hr />
            <div className="lyrics-container">
              <label>這首歌給你的感受：</label>
              <div>
                {feelingOptions.map((option, idx) => (
                  <FormControlLabel
                    key={idx}
                    control={
                      <Checkbox
                        checked={feelings.includes(option)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFeelings([...feelings, option]);
                          } else {
                            setFeelings(feelings.filter((f) => f !== option));
                          }
                        }}
                      />
                    }
                    label={option}
                  />
                ))}
              </div>
            </div>
            <div className="feel-container">
              <label>想說的話（心得）</label>
              <br />
              <textarea
                rows="3"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                style={{ width: "100%", padding: "8px", fontSize: "1rem" }}
              />
            </div>

            <div style={{ marginTop: "1rem" }}>
              <label>暱稱</label>
              <br />
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                style={{ width: "100%", padding: "8px", fontSize: "1rem" }}
              />
            </div>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowModal(false)}>取消</Button>
            <Button onClick={handleSubmit}>送出</Button>
          </DialogActions>
        </Dialog>
      </div>
    </div>
  );
};

export default LyricFeedback;
