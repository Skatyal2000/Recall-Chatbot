#llm_loader.py
from langchain.llms import HuggingFacePipeline, HuggingFaceHub
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from dotenv import load_dotenv


# def get_llm():
#     model_id = "google/flan-t5-base"
#     tokenizer = AutoTokenizer.from_pretrained(model_id)
#     model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

#     pipe = pipeline(
#         "text2text-generation",
#         model=model,
#         tokenizer=tokenizer,
#         max_new_tokens=200
#     )

#     return HuggingFacePipeline(pipeline=pipe)

load_dotenv()

def get_llm():
    return HuggingFaceHub(
        repo_id="google/flan-t5-base",
        model_kwargs={"temperature": 0.3, "max_new_tokens": 200}
    )