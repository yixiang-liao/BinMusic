import React from 'react'
import NavBar from '../layouts/NavBar'
import dayjs from 'dayjs'
import ArtistSwiper from '../layouts/ArtistSwiper'
import Titleh2 from '../components/Titleh2'
import AlbumList2 from '../components/AlbumList2'
import NewsList from '../components/NewsList'
import Footer from '../layouts/Footer'

const HomePage = () => {
  const API_BASE = import.meta.env.VITE_API_BASE_URL;

  // 📆 取得今天與一個月前的日期
  const today = dayjs().format('YYYY-MM-DD');
  const lastMonth = dayjs().subtract(2, 'month').format('YYYY-MM-DD');

  return (
    <div>
        <NavBar/>
        <ArtistSwiper/>
        <Titleh2 title="相信專輯" />
        <AlbumList2 api={`${API_BASE}/album/`} />
        <Titleh2 title="可信消息" />
        <NewsList start={lastMonth} end={today} />
        <Footer/>
    </div>
  )
}

export default HomePage
