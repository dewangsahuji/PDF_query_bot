from libs.vector_store_and_retreiver import retriever2, vectorstore
from libs.image_function import display_base64_image
from libs.connect import OPENAI_API_KEY

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from base64 import b64decode
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import uuid
from langchain_core.stores import InMemoryStore  
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_classic.retrievers.multi_vector import MultiVectorRetriever

## Execellence track
from libs.cross_modal_reranker import compute_image_similarity



import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY



store = InMemoryStore()
id_key = "doc_id"

def parse_docs(docs):
    images = []
    texts = []

    for d in docs:
        # Image/table element
        if (
            hasattr(d, "metadata")
            and hasattr(d.metadata, "image_base64")
            and d.metadata.image_base64  # ← THIS LINE FIXES IT
        ):
            images.append(d.metadata.image_base64)

        # Text document
        elif hasattr(d, "page_content"):
            texts.append(d)
        elif hasattr(d, "text"):
            texts.append(d)

    return {
        "images": images,
        "texts": texts
    }

def detect_mime_type(base64_str):
    """Detect MIME type from base64 string"""
    try:
        img_data = b64decode(base64_str)
        if img_data.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif img_data.startswith(b'\x89PNG'):
            return 'image/png'
        elif img_data.startswith(b'GIF'):
            return 'image/gif'
        else:
            return 'image/png'  # default
    except:
        return 'image/png'




def build_prompt(kwargs):

    docs_by_type = kwargs["context"]
    user_question = kwargs["question"]

    context_text = ""
    if len(docs_by_type["texts"]) > 0:
        for text_element in docs_by_type["texts"]:
            # Handle both .text and .page_content attributes
            if hasattr(text_element, 'text'):
                context_text += text_element.text + "\n"
            elif hasattr(text_element, 'page_content'):
                context_text += text_element.page_content + "\n"


    # construct prompt with context (including images)
    prompt_template = f"""
    Answer the question in pointers based only on the following context, which can include text, tables, and the below image.
    Context: {context_text}
    Question: {user_question}
    """

    prompt_content = [{"type": "text", "text": prompt_template}]

    for image in docs_by_type.get("images", []):
        try:
            mime = detect_mime_type(image)
            prompt_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime};base64,{image}"
                    },
                }
            )
        except Exception:
            # corrupted / unsupported img
            continue

    return ChatPromptTemplate.from_messages(
        [
            HumanMessage(content=prompt_content),
        ]
    )

## Excellence track
def cross_modal_rerank(query, docs, top_k=5):
    """
    Rerank documents based on their relevance to the query using CLIP embeddings.
    For images: use CLIP image-text similarity
    For text: use CLIP text-text similarity for true cross-modal comparison
    """
    scored_docs = []
    
    for idx, d in enumerate(docs):
        score = 0.0
        
        # Case 1: Document with image - use CLIP image-text similarity
        if hasattr(d, "metadata") and hasattr(d.metadata, "image_base64") and d.metadata.image_base64:
            try:
                score = compute_image_similarity(query, d.metadata.image_base64)
                # print(f"Image doc {idx}: CLIP score = {score:.4f}")
            except Exception as e:
                # print(f"Error computing image similarity: {e}")
                score = 0.0
        
        # Case 2: Text document - use CLIP text-text similarity
        elif hasattr(d, "page_content") or hasattr(d, "text"):
            text_content = d.page_content if hasattr(d, "page_content") else d.text
            
            # Use CLIP for text similarity (cross-modal reranking)
            try:
                score = compute_text_similarity(query, text_content)
                # print(f"Text doc {idx}: CLIP score = {score:.4f}")
            except Exception as e:
                # print(f"Error computing text similarity: {e}")
                # Fallback: check if retriever provided a score
                if hasattr(d, "metadata") and isinstance(d.metadata, dict) and "score" in d.metadata:
                    score = d.metadata["score"]
                else:
                    # Default score based on retriever position
                    score = 1.0 - (idx * 0.1)  # Decreasing score by position
        
        scored_docs.append((score, d))
    
    # Sort by score in descending order
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    
    # print(f"\n🔄 Reranked top {top_k} documents by relevance  ")
    # for i, (score, doc) in enumerate(scored_docs[:top_k], 1):
    #     doc_type = "image" if (hasattr(doc, "metadata") and hasattr(doc.metadata, "image_base64")) else "text"
    #     print(f"  {i}. {doc_type.upper()} - score: {score:.4f}")
    
    # Return top_k documents
    reranked = [doc for score, doc in scored_docs[:top_k]]
    
    return reranked


chain = (
    {
        "context": RunnableLambda(
            lambda q: cross_modal_rerank(q, retriever2.invoke(q))
        ) | RunnableLambda(parse_docs),
        "question": RunnablePassthrough(),
    }
    | RunnableLambda(build_prompt)
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

chain_with_sources = {
    "context": RunnableLambda(
        lambda q: cross_modal_rerank(q, retriever2.invoke(q))) | RunnableLambda(parse_docs),
    "question": RunnablePassthrough(),
} | RunnablePassthrough().assign(
    response=(
        RunnableLambda(build_prompt)
        | ChatOpenAI(model="gpt-4o-mini")
        | StrOutputParser()
    )
)


# response = chain_with_sources.invoke(
#     "What is Real Non-hydro GDP Growth?"
# )

# print("Response:", response['response'])

# print("\n\nContext:")
# for text in response['context']['texts']:
#     print(text.text)
#     print("Page number: ", text.metadata.page_number)
#     print("\n" + "-"*50 + "\n")
# for image in response['context']['images']:
#     display_base64_image(image)






