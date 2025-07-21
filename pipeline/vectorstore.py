# vectorstore.py
from langchain.vectorstores import FAISS
import os

def build_vectorstore(docs, embedder, persist_path="recall_faiss_index"):
    
    if os.path.exists(persist_path):
        print(f"Loading cached FAISS index from {persist_path}")
        vectorstore = FAISS.load_local(
            persist_path, 
            embedder, 
            allow_dangerous_deserialization=True
        ) # Loading the embedder

            
    else:
        print("Creating FAISS index from scratch")
        vectorstore = FAISS.from_documents(docs, embedder) # Creating index from scratch
        
        vectorstore.save_local(persist_path) # Saving the vector store
        print(f"FAISS index saved at {persist_path}")
        
    return vectorstore