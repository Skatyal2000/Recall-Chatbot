# rag_chain.py

# from langchain.prompts import PromptTemplate
from pipeline.llm_loader import get_llm



def build_rag_chain_manual(vectorstore):
    print("Building enhanced RAG chain")
    llm = get_llm()

    #Converts the vector store into retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    return lambda inputs: rag_pipeline(inputs, retriever, llm)

def rag_pipeline(inputs,retriever,llm):
    question = inputs["question"]
    print(f"Processing question: {question}")
    

    retrieved_docs = retriever.get_relevant_documents(question)
    #Returns the top 5 search similar to the query
    print(f"Retrieved {len(retrieved_docs)} documents")
    
    #Combines all the retrieved docs into one document block for llm
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    prompt = f"""You are a vehicle safety expert analyzing recall data. 
    Based on the recall information provided, give a comprehensive but concise answer about the recalls.

Context (Recall Information):
{context}

Question: {question}

Instructions:
- Provide a clear, informative summary of the recalls
- Mention the main safety concerns and potential consequences
- Explain what fixes or actions are typically taken
- Keep the response informative but not overly technical
- Focus on the most important safety aspects

Answer:"""
    
    # Return the final answer from llm
    answer = llm(prompt)
    
    return {
        "answer": answer.strip(),
        "source_documents": retrieved_docs
    }