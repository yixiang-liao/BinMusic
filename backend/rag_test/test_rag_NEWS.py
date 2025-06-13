from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

# 向量嵌入模型
embedding = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")

# 載入向量資料庫
vectorstore = FAISS.load_local("./faiss_db_NEWS", embedding, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

# LLM
# llm = OllamaLLM(model="gemma:2b")
# llm = OllamaLLM(model="gemma:7b")
# llm = OllamaLLM(model="llama3")
llm = OllamaLLM(model="mistral")

# PromptTemplate
prompt = PromptTemplate.from_template("""
你是一位音樂新聞小編。

請根據提供的新聞資料，用繁體中文詳細回答下方的問題。
請務必從【新聞標題】與【日期】中找線索作答。
如果新聞中完全沒有相關內容，再回答「資料中未提及」。

新聞資料如下：
=========
{context}
=========

問題：{question}

請用根據這些新聞做一個綜合整理文章。
""")
# prompt = PromptTemplate.from_template("""
# 請根據以下資料，用繁體中文詳細回答問題。
# 如果資料中沒有提及，請回答「資料中未提及」。

# =========
# {context}
# =========

# 問題：{question}
# """)

# Chain 新寫法（避免 LLMChain deprecation）
chain: RunnableSequence = prompt | llm

# 查詢
query = "2025年 麋先生最近有什麼新聞或規劃？"
docs = retriever.invoke(query)
context = "\n\n".join([doc.page_content for doc in docs])

# 🔍 印出 context 確認命中什麼
print("🔍 檢索到的內容：")
for i, doc in enumerate(docs):
    print(f"[{i}] {doc.page_content[:100]}...")

# 呼叫 LLM
result = chain.invoke({"context": context, "question": query})
print("🧠 回答：", result)
