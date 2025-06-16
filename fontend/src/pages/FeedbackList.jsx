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
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
} from "@mui/material";
import Footer from "../layouts/Footer";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const FeedbackList = () => {
  const [songs, setSongs] = useState([]);
  const [filteredSongs, setFilteredSongs] = useState([]);
  const [artists, setArtists] = useState([]);
  const [selectedArtistId, setSelectedArtistId] = useState("");
  const [searchKeyword, setSearchKeyword] = useState("");
  const [selectedSong, setSelectedSong] = useState(null);
  const [feedbacks, setFeedbacks] = useState([]);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    axios.get(`${API_BASE}/lyric_feedback/songs-with-feedback`).then((res) => {
      setSongs(res.data);
      setFilteredSongs(res.data);
    });
    axios.get(`${API_BASE}/artists`).then((res) => setArtists(res.data));
  }, []);

  useEffect(() => {
    const keyword = searchKeyword.toLowerCase();
    const filtered = songs.filter((song) => {
      const matchArtist = selectedArtistId
        ? String(song.artist_id) === String(selectedArtistId)
        : true;
      const matchKeyword =
        song.song_title.toLowerCase().includes(keyword) ||
        song.album_name.toLowerCase().includes(keyword);
      return matchArtist && matchKeyword;
    });
    setFilteredSongs(filtered);
  }, [searchKeyword, selectedArtistId, songs]);

  const parseCoverUrl = (coverJson) => {
    try {
      const parsed = JSON.parse(coverJson);
      return parsed[0]?.url || "";
    } catch {
      return "";
    }
  };

  const openFeedbackModal = (song) => {
    setSelectedSong(song);
    axios.get(`${API_BASE}/lyric_feedback/${song.lyric_id}`).then((res) => {
      setFeedbacks(res.data);
      setShowModal(true);
    });
  };

  return (
    <div className="lyric-feedback-page">
      <NavBar />
      <div className="cont">
        <Titleh2 title="回饋總覽" />

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
              <tr
                key={song.lyric_id}
                onClick={() => openFeedbackModal(song)}
                style={{ cursor: "pointer" }}
              >
                <td className="cover">
                  <img
                    src={parseCoverUrl(song.kkbox_cover)}
                    width="60"
                    height="60"
                    alt="封面"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "/default_cover.png";
                    }}
                  />
                </td>
                <td>{song.song_title}</td>
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
              {selectedSong?.song_title} - {selectedSong?.artist_name} 的回饋
            </Typography>
          </DialogTitle>
          <DialogContent>
            {feedbacks.length === 0 ? (
              <Typography>目前尚無回饋。</Typography>
            ) : (
              <List>
                {feedbacks.map((fb, idx) => (
                  <React.Fragment key={idx}>
                    <ListItem alignItems="flex-start">
                      <ListItemText
                        primary={`使用者：${fb.user_name || "匿名"}`}
                        secondary={
                          <>
                            <Typography>
                              <strong>選取歌詞：</strong>
                              {fb.selected_lyrics.join(" / ")}
                            </Typography>
                            <Typography>
                              <strong>感受：</strong>
                              {fb.feeling.join(", ")}
                            </Typography>
                            {fb.reason && (
                              <Typography>
                                <strong>心得：</strong>
                                {fb.reason}
                              </Typography>
                            )}
                          </>
                        }
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowModal(false)}>關閉</Button>
          </DialogActions>
        </Dialog>
      </div>
      <Footer />
    </div>
  );
};

export default FeedbackList;
