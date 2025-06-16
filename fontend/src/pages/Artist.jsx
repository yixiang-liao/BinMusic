import React, { useEffect, useState } from "react";
import NavBar from "../layouts/NavBar";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export default function Artist() {
  const [artists, setArtists] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/artists`)
      .then((res) => res.json())
      .then(setArtists);
  }, []);

  const rows = [];
  for (let i = 0; i < artists.length; i += 2) {
    if (artists[i + 1]) {
      rows.push([artists[i], artists[i + 1]]);
    } else {
      rows.push([artists[i]]); // 單獨一筆
    }
  }

  return (
    <div className="artist-page">
      <NavBar />
      <div className="artist-grid">
        {rows.map((row, i) => (
          <div key={i} className="artist-row">
            <a
              href={`/artist/${row[0].id}`}
              className={
                row.length === 2
                  ? `artist-card ${
                      i % 2 === 0 ? "left-narrow" : "right-narrow"
                    }`
                  : "artist-card full-width"
              }
              style={{ backgroundImage: `url(${row[0].bin_img})` }}
            >
              <div className="overlay"></div>
              <div className="info">
                <h2>{row[0].name}</h2>
                <p>{row[0].en_name}</p>
              </div>
            </a>

            {row[1] && (
              <a
                href={`/artist/${row[1].id}`}
                className={`artist-card ${
                  i % 2 === 0 ? "right-narrow" : "left-narrow"
                }`}
                style={{ backgroundImage: `url(${row[1].bin_img})` }}
              >
                <div className="overlay"></div>
                <div className="info">
                  <h2>{row[1].name}</h2>
                  <p>{row[1].en_name}</p>
                </div>
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
