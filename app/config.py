import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class Settings:
    MODEL_NAME="openai/gpt-oss-120b"
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")

settings=Settings()

def get_llm():
    return ChatGroq(model=settings.MODEL_NAME,
                    api_key=settings.GROQ_API_KEY,
                    temperature=0)