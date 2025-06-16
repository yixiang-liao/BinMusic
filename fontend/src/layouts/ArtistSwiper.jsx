import React, { useEffect, useState } from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Pagination, Autoplay } from "swiper/modules"; // ← 多了 Autoplay
import "swiper/css";
import "swiper/css/pagination";
import 'swiper/css/autoplay';
import { useRef } from "react";

const API_URL = import.meta.env.VITE_API_BASE_URL;

export default function ArtistSwiper() {
  const [artists, setArtists] = useState([]);
  const swiperRef = useRef(null);

  useEffect(() => {
    const fetchArtists = async () => {
      try {
        const response = await fetch(`${API_URL}/artists`, {
          headers: { accept: "application/json" },
        });
        const data = await response.json();
        setArtists(data);
      } catch (error) {
        console.error("Error fetching artists:", error);
      }
    };

    fetchArtists();
  }, []);

  return (
    <div className="artist-swiper-container">
      <Swiper
  modules={[Pagination, Autoplay]}
  pagination={{ dynamicBullets: true }}
  autoplay={{
    delay: 3000,
    disableOnInteraction: false,
  }}
  loop={true}
  loopAdditionalSlides={3} // ← 加這個防止 loop 出錯
  onSwiper={(swiper) => {
    // 保險手動啟動
    setTimeout(() => {
      swiper.slideToLoop(0); // ← 回到第一個 loop index
      swiper.autoplay.start();
    }, 100);
  }}
  className="mySwiper"
>
        {artists.map((artist) => (
          <SwiperSlide key={artist.id}>
            <div
              className="slide-bg"
              style={{
                backgroundImage: `url(${artist.bin_img})`,
                backgroundPosition: "top", // ← 對齊上方
              }}
              onClick={() => (window.location.href = `/artist/${artist.id}`)}
            >
              <div className="overlay" />
              <div className="slide-info">
                <h1>
                  {artist.name} {artist.en_name}
                </h1>
                <h3>{JSON.parse(artist.genres).join(" / ")}</h3>
              </div>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
}
