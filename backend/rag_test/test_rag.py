from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

# 向量嵌入模型
embedding = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-chinese")

# 載入向量資料庫
vectorstore = FAISS.load_local("./faiss_db_album", embedding, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})  # 可依需要調整 k

# 本地 LLM 模型
# llm = OllamaLLM(model="llama3")
llm = OllamaLLM(model="gemma:2b")

# PromptTemplate
prompt_template = """
請根據以下資料，用繁體中文詳細回答問題。
如果資料中沒有提及，請回答「資料中未提及」。

=========
{context}
=========

問題：{question}
"""
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template
)

# 包裝為 LLMChain
llm_chain = LLMChain(prompt=prompt, llm=llm)

# 測試查詢
query = "可以推薦給我幾首浪漫的歌曲嗎，並說明推薦的原因"
docs = retriever.get_relevant_documents(query)
context = "\n\n".join([doc.page_content for doc in docs])

# 執行
result = llm_chain.run({"context": context, "question": query})

# 顯示結果
print("🧠 回答：", result)
# print("📄 來源：")
# for doc in docs:
#     print("-", doc.page_content)
