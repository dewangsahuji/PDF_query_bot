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



def build_prompt(kwargs):

    docs_by_type = kwargs["context"]
    user_question = kwargs["question"]

    context_text = ""
    if len(docs_by_type["texts"]) > 0:
        for text_element in docs_by_type["texts"]:
            context_text += text_element.text + "\n"


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

# Execelence track
def cross_modal_rerank(query, docs):
    reranked = []
    for d in docs:
        # Case 1: LangChain Document with text
        if hasattr(d, "page_content"):
            reranked.append(d)

        # Case 2: Unstructured element with image
        elif hasattr(d, "metadata") and hasattr(d.metadata, "image_base64"):
            reranked.append(d)

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






