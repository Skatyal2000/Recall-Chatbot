#embedder.py

from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv


load_dotenv()
def get_embedder():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

