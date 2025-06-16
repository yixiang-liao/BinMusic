import { useEffect, useState } from "react";

export default function AlbumList({ api }) {
  const [albums, setAlbums] = useState([]);
  const [animatedCount, setAnimatedCount] = useState(0);

  useEffect(() => {
    fetch(api)
      .then((res) => res.json())
      .then((data) => {
        setAlbums(data);

        // 動畫：從 0 慢慢增加到 data.length
        let start = 0;
        const end = data.length;
        const duration = 1000; // 動畫持續時間（毫秒）
        const startTime = performance.now();

        const animate = (now) => {
          const elapsed = now - startTime;
          const progress = Math.min(elapsed / duration, 1); // 0 到 1
          const current = Math.floor(progress * end);
          setAnimatedCount(current);
          if (progress < 1) {
            requestAnimationFrame(animate);
          }
        };

        requestAnimationFrame(animate);
      });
  }, [api]);

  return (
    <div className="album-marquee1">
      <h3 style={{ textAlign: "center", marginBottom: "1rem" }}>
        共發行 {animatedCount} 張專輯
      </h3>
      <ul className="album-list1">
        {[...albums, ...albums].map((album, idx) => {
          const kkboxCover = JSON.parse(album.kkbox_cover || "[]");
          const cover160 = kkboxCover.find((img) => img.height === 160);
          return (
            <li key={idx} className="album-card">
              <a
                href={`/albums/${album.id}`}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <img src={cover160?.url} alt={album.album_name} />
                <div>
                  <h4>{album.album_name}</h4>
                    <p>{album.artist_name}</p>
                  <p>{album.release_date}</p>
                </div>
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
