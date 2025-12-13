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

def get_page_number(text_obj):
    """Safely get page number from text object metadata"""
    try:
        if hasattr(text_obj, 'metadata'):
            if hasattr(text_obj.metadata, 'page_number'):
                return text_obj.metadata.page_number
            elif isinstance(text_obj.metadata, dict):
                return text_obj.metadata.get('page_number', 'N/A')
        return 'N/A'
    except:
        return 'N/A'

def get_page_content(text_obj):
    """Safely get page content from text object"""
    try:
        if hasattr(text_obj, 'page_content'):
            return text_obj.page_content
        elif hasattr(text_obj, 'text'):
            return text_obj.text
        else:
            return str(text_obj)
    except:
        return "Unable to extract content"

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
                        page_num = get_page_number(text)
                        content = get_page_content(text)
                        
                        st.markdown(f"**Source {i}** (Page {page_num})")
                        st.text(content[:500] + "..." if len(content) > 500 else content)
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
                    
                    # st.write("DEBUG context keys:", context.keys())
                    # st.write("DEBUG num images:", len(context.get("images", [])))
                    # st.write("DEBUG num texts:", len(context.get("texts", [])))

                    # Display text sources
                    if context["texts"]:
                        st.subheader("Text Sources")
                        for i, text in enumerate(context["texts"], 1):
                            page_num = get_page_number(text)
                            content = get_page_content(text)
                            
                            st.markdown(f"**Source {i}** (Page {page_num})")
                            st.text(content[:500] + "..." if len(content) > 500 else content)
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
                                    st.image(img,
                                    caption=f"Image {i+1}",
                                    use_container_width=True,
                                    )
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
    """)