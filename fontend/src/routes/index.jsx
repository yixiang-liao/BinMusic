// routes/index.jsx
import { Routes, Route } from 'react-router-dom';
import HomePage from '../pages/HomePage';
import ArtistDetailPage from '../pages/ArtistDetailPage';
import AlbumDetailPage from '../pages/AlbumDetailPage';
import Artist from '../pages/Artist';
import Album from '../pages/Album';
import News from '../pages/News';
import AIBout from '../pages/AIBout';
import LyricFeedback from '../pages/LyricFeedback';
import FeedbackList from '../pages/FeedbackList';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/artist/" element={<Artist />} />
      <Route path="/artist/:id" element={<ArtistDetailPage />} />
      <Route path="/album/" element={<Album />} />
      <Route path="/albums/:id" element={<AlbumDetailPage />} />
      <Route path="/News/" element={<News />} />
      <Route path="/AIBout/" element={<AIBout />} />
      <Route path="/LyricFeedback/" element={<LyricFeedback />} />
      <Route path="/FeedbackList/" element={<FeedbackList />} />
    </Routes>
  );
};

export default AppRoutes;
