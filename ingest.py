import os
import json
from sentence_transformers import SentenceTransformer
import pypandoc
import pinecone
import pymilvus
import dotenv
from pymilvus import connections, FieldSchema, Collection , CollectionSchema, DataType
dotenv.load_dotenv()

VECTOR_DB = os.getenv("VECTOR_DB", "local")
model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks,i = [], 0
    while i < len(words):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap

    return chunks

def prepare_chunks(source_id, text):
    chunks = chunk_text(text)
    records = []
    for idx, c in enumerate(chunks):
        emb = model.encode(c).tolist()
        records.append({
            "id":f"{source_id}_chunk_{idx}",
            "embedding": emb,
            "text": c,
            "meta":{"source": source_id}
        })
    return records


if __name__ == "__main__":
    with open("sauravkumar.txt", "r", encoding="utf-8") as f:
         resume_text = f.read()
    resume_text = resume_text.replace("\n", " ")    
    # chunks = prepare_chunks("resume", resume_text)
    records = prepare_chunks("resume", resume_text)
    print(json.dumps(records, indent=2))

    if VECTOR_DB == "pinecone":
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
        index = pinecone.Index("resume-bot")
        vectors = [(r['id'],r['embedding'], {"text": r['text'],"source":r['meta']['source']}) for r in records]
        index.upsert(vectors)
    if VECTOR_DB == "milvus":
        pass