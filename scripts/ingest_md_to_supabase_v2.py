import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
import tiktoken
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
import numpy as np

# Load .env variables
load_dotenv()

# Constants
DATA_DIR = Path(__file__).parent.parent / "personal_vault"
CHUNK_TOKEN_SIZE = 500
BATCH_SIZE = 50

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


tokenizer = tiktoken.get_encoding("cl100k_base")
print(f"Loading embedding model: {EMBEDDING_MODEL}...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print(f"Embedding model loaded. Dimension: {embedding_model.get_sentence_embedding_dimension()}")

def chunk_text(text: str, max_tokens: int = CHUNK_TOKEN_SIZE) -> List[str]:
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = len(tokenizer.encode(word))
        if current_tokens + word_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def embed_texts(texts: List[str]) -> List[List[float]]:





    try:
        embeddings = embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    except Exception as e:
        return {
            "tool_result": {"error": f"Embedding generation failed: {str(e)}"},
            "tool_id": "embed_texts"
        }

def process_file(file_path: Path) -> List[Dict[str, Any]]:



    try:
        text = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(text, max_tokens=CHUNK_TOKEN_SIZE)
        embeddings = embed_texts(chunks)












        records = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            records.append({
                "url": str(file_path),
                "content": chunk,
                "summary": chunk[:100],
                "source": "personal_vault",
                "embedding": embedding,
                "file_name": file_path.name
            })
        return records
    except Exception as e:
        return {
            "tool_result": {"error": f"File processing failed: {str(e)}"},
            "tool_id": "process_file"
        }






def upsert_records(records: List[Dict[str, Any]]):
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i+BATCH_SIZE]
        try:
            response = supabase.table("crawled_pages").upsert(batch).execute()
            print(f"✅ Upserted batch {i//BATCH_SIZE + 1}/{(len(records) + BATCH_SIZE - 1)//BATCH_SIZE}")
        except Exception as e:
            print(f"❌ Failed to upsert batch starting at {i}: {e}")






















def main():
    print("🚀 Starting ingestion with sentence-transformers...")
    print(f"📁 Data directory: {DATA_DIR}")
    
    if not Path(DATA_DIR).exists():
        print(f"❌ Data directory does not exist: {DATA_DIR}")
        print("Creating directory...")
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    md_files = list(Path(DATA_DIR).rglob("*.md"))
    print(f"📂 Found {len(md_files)} markdown file(s) to process.")
    
    if len(md_files) == 0:
        print("⚠️ No markdown files found. Please add .md files to the personal_vault directory.")
        return
    
    # Remove test mode limitation - process all files
    all_records = []
    for i, file_path in enumerate(md_files, 1):
        print(f"\n📄 Processing file {i}/{len(md_files)}: {file_path.name}")
        try:
            records = process_file(file_path)
            all_records.extend(records)
            print(f"   ✅ Generated {len(records)} chunks")
        except Exception as e:
            print(f"   ⚠️ Error processing {file_path}: {e}")

    print(f"\n📦 Total chunks to upsert: {len(all_records)}")
    if all_records:
        upsert_records(all_records)
        print("✅ Ingestion completed successfully!")
    else:
        print("❌ No records to upsert.")

if __name__ == "__main__":
    main()
