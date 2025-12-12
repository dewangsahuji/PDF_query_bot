from libs.connect import OPENAI_API_KEY
from libs.get_data import texts, tables, images
from libs.summaries import *
import os

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

import uuid
from langchain_core.stores import InMemoryStore  
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_classic.retrievers.multi_vector import MultiVectorRetriever


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


store = InMemoryStore()
id_key = "doc_id"

embeddings = OpenAIEmbeddings()

embedding_dim = len(embeddings.embed_query("hello world"))
index = faiss.IndexFlatL2(embedding_dim)


# ----------------------------------------------------
# Vector Store and Retreiver
# ----------------------------------------------------

vectorstore = FAISS(
    embedding_function=OpenAIEmbeddings(),
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

retriever2 = MultiVectorRetriever(
    vectorstore=vectorstore,
    docstore=store,
    id_key=id_key,
    # persist_directory=r"C:\Users\dewan\Coding\MLOps\IAI_Solutions\FAISS_IAI_VS101"    
)


# ----------------------------------------------------
# Add texts
# ----------------------------------------------------

doc_ids = [str(uuid.uuid4()) for _ in texts]
summary_texts = [
    Document(page_content=summary, metadata={id_key: doc_ids[i]}) for i, summary in enumerate(text_summaries)
]
retriever2.vectorstore.add_documents(summary_texts)
retriever2.docstore.mset(list(zip(doc_ids, texts)))
# print("Documents added:", retriever2.vectorstore.index.ntotal)


# Add tables
table_ids = [str(uuid.uuid4()) for _ in tables]
summary_tables = [
    Document(page_content=summary, metadata={id_key: table_ids[i]}) for i, summary in enumerate(table_summaries)
]
retriever2.vectorstore.add_documents(summary_tables)
retriever2.docstore.mset(list(zip(table_ids, tables)))
# print("Documents added:", retriever2.vectorstore.index.ntotal)


# Add image summaries
img_ids = [str(uuid.uuid4()) for _ in images]
summary_img = [
    Document(page_content=summary, metadata={id_key: img_ids[i]}) for i, summary in enumerate(image_summaries)
]
retriever2.vectorstore.add_documents(summary_img)
retriever2.docstore.mset(list(zip(img_ids, images)))
# print("Documents added:", retriever2.vectorstore.index.ntotal)













