from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# 嵌入模型要和你建立 vectorstore 時一致
embedding = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")

# 載入你的 vectorstore
vectorstore = FAISS.load_local("./faiss_db_NEWS", embedding, allow_dangerous_deserialization=True)

# 拿出所有文件（若使用 from_documents 建立過就可以）
docs = vectorstore.docstore._dict  # dict of document_id -> Document

# 檢查所有內容
for i, (doc_id, doc) in enumerate(docs.items()):
    content = doc.page_content
    if "2025" in content or "最近" in content or "今年" in content:
        print(f"✅ 第 {i} 筆命中：")
        print(content[:200])
        print("------")
