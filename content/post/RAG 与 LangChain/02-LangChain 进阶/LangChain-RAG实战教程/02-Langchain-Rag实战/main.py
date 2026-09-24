import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader

# 加载文本文件
loader = TextLoader("./example_doc.txt", encoding="utf-8") # 替换为您的文本文件路径

# 或者加载 PDF 文件
# loader = PyPDFLoader("./sample.pdf") # 替换为您的 PDF 文件路径
documents = loader.load()

# 打印加载的文档数量和第一个文档的内容（部分）
print(f"加载了 {len(documents)} 个文档")
if documents:
    print(f"第一个文档的内容预览: {documents[0].page_content[:200]}")



from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# 打印分割后的文本块数量和第一个文本块的内容（部分）
print(f"文档被分割成 {len(texts)} 个文本块")
if texts:
    print(f"第一个文本块的内容预览: {texts[0].page_content[:200]}")


from langchain_community.embeddings import DashScopeEmbeddings



        # Initialize the embeddings model
embeddings_model =  DashScopeEmbeddings(
    model="text-embedding-v2",
    # other params...
)


# 嵌入示例文本 (可选，仅为演示)
example_text = "这是一个示例文本，用于测试嵌入模型。"
example_embedding = embeddings_model.embed_query(example_text)
print(f"示例文本的嵌入向量 (部分): {example_embedding[:5]}")

from langchain_community.vectorstores import Chroma

# 创建向量存储，并将文本块及其嵌入存储进去
# persist_directory 参数指定了向量数据库在磁盘上持久化存储的路径
vectorstore = Chroma.from_documents(documents=texts,
                                    embedding=embeddings_model,
                                    persist_directory="./chroma_db")

# 持久化向量存储到磁盘 (Chroma 在创建时会自动持久化，但显式调用 ensure_persisted() 是个好习惯)
vectorstore.persist()

print("向量存储创建并持久化成功！")

# 如果你之前已经创建并持久化了向量数据库，可以这样加载它：
# from langchain_community.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings

# embeddings_model = OpenAIEmbeddings()
# vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings_model)
# print("从磁盘加载向量存储成功！")





retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # k 表示检索最相关的 k 个文本块

# 测试检索器 (可选)
query = "什么是 Langchain?"
relevant_docs = retriever.get_relevant_documents(query)
print(f"\n对于查询 '{query}', 检索到的相关文档数量: {len(relevant_docs)}")
for i, doc in enumerate(relevant_docs):
    print(f"相关文档 {i+1}:\n{doc.page_content[:150]}...\n")




from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
)



from langchain.chains import RetrievalQA

# 创建 RetrievalQA 链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff", # "stuff" 是最简单的链类型，将所有检索到的文本直接放入提示中
    retriever=retriever,
    return_source_documents=True # 是否返回源文档
)

# 其他 chain_type 选项包括:
# "map_reduce": 分别处理每个文档，然后合并结果
# "refine": 依次处理每个文档，逐步优化答案
# "map_rerank": 分别处理每个文档，并根据置信度对结果进行排序


query = "请介绍一下 Langchain 的主要功能。" # 替换为您想问的问题
result = qa_chain.invoke({"query": query})

print("\n模型生成的回答:")
print(result["result"])

print("\n引用的源文档:")
for i, source_doc in enumerate(result["source_documents"]):
    print(f"源文档 {i+1} (来自: {source_doc.metadata.get('source', '未知来源')}, 页码: {source_doc.metadata.get('page', 'N/A')}):") # 假设元数据中有 'source' 和 'page'
    print(f"{source_doc.page_content[:200]}...\n")


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. 定义提示模板
template = """请根据以下上下文信息来回答问题。如果你不知道答案，就说你不知道，不要试图编造答案。
用最多三句话来回答，并保持答案简洁。

上下文:
{context}

问题: {question}

有用的回答:"""
prompt = ChatPromptTemplate.from_template(template)

# 2. 定义如何格式化检索到的文档
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 3. 构建 RAG 链
rag_chain_lcel = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 4. 进行提问
query_lcel = "Langchain 的核心组件有哪些？"
answer_lcel = rag_chain_lcel.invoke(query_lcel)

print(f"\n使用 LCEL 构建的 RAG 链，对于查询 '{query_lcel}' 的回答:")
print(answer_lcel)

# 如果你想同时获取源文档，可以这样构建：
from operator import itemgetter

rag_chain_with_source = RunnablePassthrough.assign(
    context=itemgetter("question") | retriever | format_docs
).assign(
    answer= (
        {"context": itemgetter("context"), "question": itemgetter("question")}
        | prompt
        | llm
        | StrOutputParser()
    )
)

result_lcel_with_source = rag_chain_with_source.invoke({"question": query_lcel})

print("\n使用 LCEL (包含源文档) 的回答:")
print(result_lcel_with_source["answer"])
# print("\n引用的上下文 (LCEL):") # context 实际上是格式化后的检索文档字符串
# print(result_lcel_with_source["context"][:500] + "...")
