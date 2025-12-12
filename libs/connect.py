# import os
# from dotenv import load_dotenv
# load_dotenv()

# OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

# # Add validation to ensure the key was loaded
# if OPENAI_API_KEY is None:
#     raise ValueError(
#         "OPENAI_API_KEY not found in environment variables. "
#         "Please create a .env file with OPENAI_API_KEY=your_key_here"
#     )

import streamlit as st
import os

# Function to safely get API key
def get_api_key():
    # Try Streamlit Cloud secrets first
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    
    # Try local .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("OPENAI_API_KEY")
    except ImportError:
        return None

# Get the API key
OPENAI_API_KEY = get_api_key()

# Validate
if not OPENAI_API_KEY:
    st.error("""
        OPENAI_API_KEY not found. Please configure it:
        
        **For Streamlit Cloud:**
        1. Go to app settings → Secrets
        2. Add: OPENAI_API_KEY = "your-key"
        
        **For Local Development:**
        1. Create a .env file
        2. Add: OPENAI_API_KEY=your-key
    """)
    st.stop()

# Your app code continues here...
st.success("API Key loaded successfully!")