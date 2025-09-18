import os
import openai
from fastapi import FastAPI
from pydantic import BaseModel
import pinecone
import dotenv
VECTOR_DB = os.getenv("VECTOR_DB", "local")

dotenv.load_dotenv()

if VECTOR_DB == "pinecone":
    pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
    index = pinecone.Index("resume-bot")

elif VECTOR_DB == "milvus":
    pass

