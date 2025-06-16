import React, { useEffect, useState } from "react";
import NavBar from "../layouts/NavBar";
import Titleh2 from "../components/Titleh2";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const Album = () => {
  const [albums, setAlbums] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/album/`)
      .then((res) => res.json())
      .then(setAlbums)
      .catch((err) => console.error("專輯資料載入失敗", err));
  }, []);

  return (
    <div className="album-page">
      <NavBar />
      <div className="cont">
        <Titleh2 title="相信專輯" />
        <div className="album-grid">
          {albums.map((album) => {
            const kkboxCovers = JSON.parse(album.kkbox_cover || "[]");
            const cover =
              kkboxCovers.find((img) => img.height === 160) || kkboxCovers[0];

            return (
              <a
                href={`/albums/${album.id}`}
                key={album.id}
                className="album-card"
              >
                <img src={cover?.url} alt={album.album_name} />
                <div className="album-info">
                  <h3>{album.album_name}</h3>
                  <p>{album.release_date}</p>
                  <p>{album.artist?.name}</p>
                </div>
              </a>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Album;
