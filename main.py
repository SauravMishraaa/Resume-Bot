import os
import dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import google.generativeai as genai

dotenv.load_dotenv()

VECTOR_DB = os.getenv("VECTOR_DB", "pinecone")  

embedder = SentenceTransformer("all-MiniLM-L6-v2")

if VECTOR_DB == "pinecone":
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("resume-bot")
elif VECTOR_DB == "milvus":
    pass

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query(req: QueryRequest):
    q_text = req.query
    print(f"Person asked: {q_text}")

    
    q_emb = embedder.encode(q_text).tolist()

    if VECTOR_DB == "pinecone":
        res = index.query(vector=q_emb, top_k=5, include_metadata=True)
        contexts = "\n\n".join([m["metadata"]["text"] for m in res["matches"]])
    else:
        contexts = ""

    prompt = (
    "You are Saurav Kumar's AI resume assistant. "
    "Your role is to help recruiters and professionals learn about Saurav's skills, projects, and experience. "
    "Answer the question in detail using the provided context. "
    "If the question cannot be answered from the context, respond with: "
    "'I’m Saurav Kumar’s AI resume assistant and can only answer questions about his skills, projects, and experience.'\n\n"
    f"Context:\n{contexts}\n\n"
    f"Question:\n{q_text}\n\n"
    "Answer in a clear, professional tone. Use short paragraphs or bullet points for readability. "
    "Do not repeat the question."
)



    response = gemini_model.generate_content(prompt)
    return {"answer": response.text}
