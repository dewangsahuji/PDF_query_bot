import streamlit as st
from libs.RAG import chain_with_sources
from libs.image_function import display_base64_image
import base64
from io import BytesIO
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="PDF Query Bot",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 PDF Query Bot")
st.markdown("Ask questions about your document and get AI-powered answers with sources.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display sources if available
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📄 View Sources"):
                sources = message["sources"]
                
                # Display text sources
                if sources["texts"]:
                    st.subheader("Text Sources")
                    for i, text in enumerate(sources["texts"], 1):
                        st.markdown(f"**Source {i}** (Page {text.metadata.get('page_number', 'N/A')})")
                        st.text(text.page_content[:500] + "..." if len(text.page_content) > 500 else text.page_content)
                        st.divider()
                
                # Display image sources
                if sources["images"]:
                    st.subheader("Image Sources")
                    cols = st.columns(min(len(sources["images"]), 3))
                    for i, img_b64 in enumerate(sources["images"]):
                        with cols[i % 3]:
                            try:
                                img_data = base64.b64decode(img_b64)
                                img = Image.open(BytesIO(img_data))
                                st.image(img, caption=f"Image {i+1}", use_container_width=True)
                            except Exception as e:
                                st.error(f"Error displaying image: {str(e)}")

# Chat input
if prompt := st.chat_input("Ask a question about your document..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response with spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Get response from RAG chain
                result = chain_with_sources.invoke(prompt)
                response = result["response"]
                context = result["context"]
                
                # Display response
                st.markdown(response)
                
                # Store message with sources
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": context
                })
                
                # Display sources in expander
                with st.expander("📄 View Sources"):
                    # Display text sources
                    if context["texts"]:
                        st.subheader("Text Sources")
                        for i, text in enumerate(context["texts"], 1):
                            st.markdown(f"**Source {i}** (Page {text.metadata.get('page_number', 'N/A')})")
                            st.text(text.page_content[:500] + "..." if len(text.page_content) > 500 else text.page_content)
                            st.divider()
                    
                    # Display image sources
                    if context["images"]:
                        st.subheader("Image Sources")
                        cols = st.columns(min(len(context["images"]), 3))
                        for i, img_b64 in enumerate(context["images"]):
                            with cols[i % 3]:
                                try:
                                    img_data = base64.b64decode(img_b64)
                                    img = Image.open(BytesIO(img_data))
                                    st.image(img, caption=f"Image {i+1}", use_container_width=True)
                                except Exception as e:
                                    st.error(f"Error displaying image: {str(e)}")
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This PDF Query Bot uses Retrieval-Augmented Generation (RAG) to answer questions about your document.
    
    **Features:**
    - 🔍 Semantic search across text, tables, and images
    - 📊 View source documents for each answer
    - 🖼️ Image-based question answering
    - 💬 Chat history maintained during session
    """)
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.markdown("### 📝 Example Questions")
    st.markdown("""
    - What is Real Non-hydro GDP Growth?
    - Summarize the key findings in the document
    - What information is shown in the tables?
    - Explain the trends shown in the images
    """)