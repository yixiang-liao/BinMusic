import React, { useState, useEffect, useRef } from "react";
import NavBar from "../layouts/NavBar";
import Titleh2 from "../components/Titleh2";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const ENDPOINTS = {
  album: `${API_BASE}/rag/stream/ask/album`,
  news: `${API_BASE}/rag/stream/ask/news`,
};

const AIBout = () => {
  const [tab, setTab] = useState("album");
  const [question, setQuestion] = useState("");
  const [chatLog, setChatLog] = useState(() => {
    return JSON.parse(localStorage.getItem("chatLog")) || [];
  });
  const [loading, setLoading] = useState(false);
  const messageEndRef = useRef(null);
  const [expandedIndexes, setExpandedIndexes] = useState({}); // 新增：控制展開狀態
  const inputRef = useRef(null);

  useEffect(() => {
    localStorage.setItem("chatLog", JSON.stringify(chatLog));
  }, [chatLog]);

  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
    if (inputRef.current) {
      inputRef.current.focus(); // 自動 focus
    }
  }, [chatLog, loading]);
  const formatAnswerText = (text) => {
  if (!text) return '';

  return text
    .replace(/\*\*(.+?)\*\*/g, '<br /><strong>$1</strong>') // 粗體 + 斷行
    .replace(/\*\s*(.+?)(?=(\n|\*|<|$))/g, '<br />• $1') // 星號條列 + 斷行
    .replace(/。(?=\s*[^\n])/g, '。<br />') // 每句句號換行（若不是已經換行）
    .replace(/<b>(.*?)<\/b>/g, '<strong>$1</strong>') // <b> 轉 <strong>
    .replace(/(<br \/>){2,}/g, '<br />') // 移除多餘 <br />
    .trim();
};

  const handleAsk = async () => {
    if (!question.trim()) return;

    const currentQuestion = question; // ✅ 備份輸入內容
    setQuestion(""); // ✅ 馬上清空輸入欄位
    setChatLog((prev) => [...prev, { type: "user", text: currentQuestion }]);
    setLoading(true);

    const response = await fetch(ENDPOINTS[tab], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: currentQuestion }), // ✅ 使用備份的值
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let answer = "";
    let sources = [];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.trim()) continue;
        const parsed = JSON.parse(line);

        if (parsed.type === "source") {
          sources = parsed.data;
        } else if (parsed.type === "answer") {
          answer += parsed.data;
          setChatLog((prev) => {
            const last = prev[prev.length - 1];
            if (last?.type === "streaming") {
              return [
                ...prev.slice(0, -1),
                { type: "streaming", text: answer, sources },
              ];
            } else {
              return [...prev, { type: "streaming", text: answer, sources }];
            }
          });
        }
      }
    }

    setLoading(false);
    setChatLog((prev) => [
      ...prev.slice(0, -1),
      { type: "bot", text: answer, sources },
    ]);
  };

  const handleClear = () => {
    setChatLog([]);
    localStorage.removeItem("chatLog");
  };

  const toggleExpand = (msgIdx, srcIdx) => {
    setExpandedIndexes((prev) => ({
      ...prev,
      [`${msgIdx}-${srcIdx}`]: !prev[`${msgIdx}-${srcIdx}`],
    }));
  };

  return (
    <div className="aibout-page">
      <NavBar />
      <div className="cont">
        <Titleh2 title="Bin Music LLM" />
        <div className="chat-tabs">
          <button
            className={tab === "album" ? "active" : ""}
            onClick={() => setTab("album")}
          >
            專輯
          </button>
          <button
            className={tab === "news" ? "active" : ""}
            onClick={() => setTab("news")}
          >
            新聞
          </button>
        </div>

        <div className="chat-box">
          {chatLog.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.type}`}>
              <div
  className="text"
  dangerouslySetInnerHTML={{ __html: formatAnswerText(msg.text) }}
/>
              {msg.sources && (
                <div
                  className="sources"
                  onClick={() =>
                    setExpandedIndexes((prev) => ({
                      ...prev,
                      [idx]: !prev[idx],
                    }))
                  }
                  style={{ cursor: "pointer" }}
                >
                  <div style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>
                    點此展開/摺疊參考資料（共 {msg.sources.length} 筆）
                  </div>
                  {expandedIndexes[idx] &&
                    msg.sources.map((s, i) => (
                      <div key={i} className="source-item">
                        <strong>{s.title}</strong>
                        <div className="source-content">{s.content}</div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="chat-message loading">打字中...</div>}
          <div ref={messageEndRef} />
        </div>

        <div className="chat-input">
          <input
            ref={inputRef}
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            // onKeyDown={e => {
            //   if (e.key === 'Enter') {
            //     e.preventDefault();  // 避免表單預設送出動作
            //     handleAsk();
            //   }
            // }}
            placeholder="請輸入問題..."
          />
          <button onClick={handleAsk}>送出</button>
          <button onClick={handleClear} className="clear-btn">
            清空
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIBout;
