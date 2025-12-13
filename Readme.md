# PDF Query Bot

## 🤖 Ask Me Anything: Your PDF Assistant

The **PDF Query Bot** is a powerful application that allows you to chat with 2024 ARTICLE IV CONSULTATION—PRESS RELEASE STAFF REPORT AND STATEMENT BY THE EXECUTIVE DIRECTOR FOR QATAR. Get answers to your questions by advanced Retrieval-Augmented Generation (RAG) techniques.

## ✨ Features

  * **Intelligent Q\&A:** Get accurate, context-aware answers to questions based *only* on the content of uploaded PDF.
  * **Multi-Page Support:** Process and query large, multi-page PDF document effortlessly.
  * **Context Preservation:** Utilizes vector stores to efficiently retrieve relevant text snippets, ensuring answers are precise and verifiable.
  * **Simple Web Interface:** A user-friendly interface built with Streamlit for easy interaction.

## 🚀 Technologies Used

This project is built using Python and leverages several key libraries from the AI/ML ecosystem:

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Interface** | `Streamlit` |UI|
| **PDF Processing** | `Unstructured` | Handles reading and extracting text from PDF files. |
| **Text Chunking** | `LangChain` |LLM handling and RAG  |
| **Embeddings** | `OpenAI Embeddings` | Embeddings |
| **Vector Store** | `FAISS`, `ChromaDB`,  | Retreivers |
| **Language Model** | `OpenAI GPT-4o-mini` ,`llama-3.1-8b-instant` | Generate answers. |

## 🛠️ Installation and Setup

Follow these steps to get the project running on your local machine.

### Prerequisites

  * Python 3.11+

### Step 1: Clone the repository

```bash
git clone https://github.com/dewangsahuji/PDF_query_bot.git
cd PDF_query_bot
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
# venv\Scripts\activate   # On Windows
```

### Step 3: Install Dependencies

All required Python packages are listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

You need to set your API key as an environment variable. Create a file named `.env` in the root directory and add your key:

**.env**

```
OPENAI_API_KEY="YOUR_API_KEY_HERE"
# Or if using a different LLM/service, adjust the key name
```

*(Note: You will need to install a package like `python-dotenv` and load it in your `app2.py` for this file to be recognized.)*

## 💻 Usage

Run the main application file using Streamlit:

```bash
streamlit run app2.py
```

The application will automatically open in your web browser (usually at `http://localhost:8501`).

1.  **Upload:** Use the interface to upload your desired PDF document.
2.  **Process:** The bot will automatically chunk and index the document.
3.  **Query:** Type your question in the chat interface and receive an answer drawn from the PDF content.

## 📂 Project Structure

| File/Folder | Description |
| :--- | :--- |
| `app2.py` | The main Streamlit application file containing the user interface and core logic. |
| `requirements.txt` | A list of all Python libraries needed for the project. |
| `chunks.json` | (Likely) Stores pre-processed text chunks or metadata. |
| `prototyp3.ipynb` | A Jupyter Notebook used for initial prototyping and testing of the LLM/RAG pipeline. |
| `Data/` | Directory for sample or pre-loaded PDF files. |
| `libs/` | (Likely) Contains custom Python modules or utility functions. |

## 🤝 Contributing

Contributions are welcome\! If you have suggestions for improvements, or find a bug, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/improvement`).
3.  Commit your changes (`git commit -m 'feat: added a new feature'`).
4.  Push to the branch (`git push origin feature/improvement`).
5.  Open a Pull Request.

## 📜 License


-----

*(End of README.md)*
