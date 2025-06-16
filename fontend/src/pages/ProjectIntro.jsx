import React, { useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import NavBar from "../layouts/NavBar";
import Footer from "../layouts/Footer";

export default function ProjectIntro() {
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState({ title: "", img: "", desc: "" });

  const openModal = (title, img, desc) => {
    setModalData({ title, img, desc });
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
  };

  return (
    <div className="project-intro">
      <NavBar />
      {/* 1. 封面區 */}
      <section className="cover">
        <div className="cover-overlay" />
        <div className="cover-text">
          <h1>BinMusic 相信音樂 大數據分析平台</h1>
          <p>讓資料與 AI 為華語音樂寫下新的篇章</p>
          <a href="/" target="_blank" rel="noreferrer">前往網站</a>
        </div>
      </section>

      {/* 2. 系統簡介區 */}
      <section className="intro">
        <div className="intro-text">
          <h2>平台介紹</h2>
          <p>
            結合音樂資料分析與 AI 問答的互動平台，整合 KKBOX、Spotify、BinMusic官網資訊，透過 NLP 與 RAG 架構，提供更有深度的音樂探索體驗。
          </p>
        </div>
      </section>

      {/* 3. 前端模組區 */}
      <section className="modules">
        <h2>前端模組功能</h2>
        <div className="module-grid">
          {[
            {
              title: "藝人專區",
              img: "/images/藝人頁面.png",
              desc: "瀏覽藝人介紹、代表作品、新聞曝光與歌詞分析。",
            },
            {
              title: "專輯專區",
              img: "/images/專輯頁面.png",
              desc: "顯示專輯資訊、收錄歌曲與情感分析圖表。",
            },
            {
              title: "新聞專區",
              img: "/images/新聞專區.png",
              desc: "新聞篩選、趨勢圖與文字雲，快速掌握動態。",
            },
            {
              title: "BinMusic LLM",
              img: "/images/BinMusicLLM.png",
              desc: "串接本地大模型，提供音樂與新聞相關問答。",
            },
            {
              title: "歌詞互動",
              img: "/images/歌詞互動.png",
              desc: "選取觸動人心的歌詞段落，填寫心得，建立歌詞感受資料集。",
            },
            {
              title: "歌詞回饋",
              img: "/images/歌詞回饋.png",
              desc: "瀏覽其他使用者對歌曲歌詞的回饋與感受，形成音樂共鳴社群。",
            },
          ].map((mod) => (
            <div
              key={mod.title}
              className="module-card"
              onClick={() => openModal(mod.title, mod.img, mod.desc)}
            >
              <img src={mod.img} alt={mod.title} />
              <h3>{mod.title}</h3>
              <p>{mod.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 4. 後端與 RAG 區 */}
      <section className="backend">
        <div className="backend-block">
          <div className="text">
            <h2>後端資料處理</h2>
            <p>整合 KKBOX/Spotify API、BinMusic 爬蟲、斷詞、詞性、NER 與情感分析模型，結合 SQLite 資料庫管理。</p>
          </div>
          <div className="image">
            <img src="/images/BackEnd.png" alt="資料處理流程圖" />
          </div>
        </div>
        <div className="backend-block reverse">
          <div className="text">
            <h2>RAG 問答系統</h2>
            <p>
              使用 shibing624/text2vec-base-chinese 中文向量模型與 FAISS 建立向量庫，透過本地 LLM（Gemma3:4b-it-qat）實現即時音樂問答與新聞查詢。
            </p>
          </div>
          <div className="image">
            <img src="/images/RAG.png" alt="RAG 流程圖" />
          </div>
        </div>
      </section>

      {/* MUI Modal */}
      <Dialog
        open={modalOpen}
        onClose={closeModal}
        maxWidth={false}
        PaperProps={{ sx: { width: 1050 } }}
      >
        <DialogTitle>
          {modalData.title}
          <IconButton
            aria-label="close"
            onClick={closeModal}
            sx={{ position: "absolute", right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <img
            src={modalData.img}
            alt={modalData.title}
            style={{ width: "1000px", borderRadius: "8px", marginBottom: "1rem", display: "block", marginLeft: "auto", marginRight: "auto" }}
          />
          <DialogContentText>{modalData.desc}</DialogContentText>
        </DialogContent>
      </Dialog>
      <Footer />

      {/* 5. 聯絡我們區 */}
    </div>
  );
}
