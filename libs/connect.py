import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

# Add validation to ensure the key was loaded
if OPENAI_API_KEY is None:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please create a .env file with OPENAI_API_KEY=your_key_here"
    )

