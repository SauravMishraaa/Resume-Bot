import os
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import dotenv

dotenv.load_dotenv()

VECTOR_DB = os.getenv("VECTOR_DB", "pinecone")
model = SentenceTransformer('all-MiniLM-L6-v2')

def chunk_text(text, chunk_size=350, overlap=50):
    words = text.split()
    chunks, i = [], 0
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
            "id": f"{source_id}_chunk_{idx}",
            "embedding": emb,
            "text": c,
            "meta": {"source": source_id}
        })
    return records

def process_csv(file_path, source_name):
    df = pd.read_csv(file_path)
    records = []
    for i, row in df.iterrows():
        row_text = " ".join([f"{col}: {row[col]}" for col in df.columns if pd.notnull(row[col])])
        row_records = prepare_chunks(f"{source_name}_row_{i}", row_text)
        records.extend(row_records)
    return records

if __name__ == "__main__":
    all_records = []

    if os.path.exists("sauravkumar.txt"):
        print("📄 Ingesting resume...")
        with open("sauravkumar.txt", "r", encoding="utf-8") as f:
            resume_text = f.read().replace("\n", " ")
        all_records.extend(prepare_chunks("resume", resume_text))

    
    csv_folder = "linkedin_data"  
    if os.path.isdir(csv_folder):
        for file_name in os.listdir(csv_folder):
            if file_name.endswith(".csv"):
                file_path = os.path.join(csv_folder, file_name)
                source_name = os.path.splitext(file_name)[0] 
                print(f"📥 Ingesting {file_name}...")
                all_records.extend(process_csv(file_path, source_name))

    print(f"✅ Total records prepared: {len(all_records)}")

    
    if VECTOR_DB == "pinecone" and all_records:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = "resume-bot"

        if index_name not in pc.list_indexes().names():
            pc.create_index(
                index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=os.getenv("PINECONE_CLOUD"),
                    region=os.getenv("PINECONE_REGION")
                )
            )

        index = pc.Index(index_name)

        vectors = [
            (r['id'], r['embedding'], {"text": r['text'], "source": r['meta']['source']})
            for r in all_records
        ]
        index.upsert(vectors)
        print(f"🚀 Upserted {len(vectors)} records to Pinecone")
