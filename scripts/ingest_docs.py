# scripts/ingest_docs.py
import os, json, time
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import openai
from tqdm import tqdm

load_dotenv()  # pulls keys from .env

DATA_DIR = Path(r"C:\AI_SecondBrain\UltimateAI\data\docs")
BATCH_SIZE = 20            # tune if you hit rate limits
MODEL = "text-embedding-ada-002"

supabase = create_client(os.environ["SUPABASE_URL"],
                         os.environ["SUPABASE_SERVICE_KEY"])
openai.api_key = os.environ["OPENAI_API_KEY"]

def embed_batch(texts):
    """Call OpenAI embeddings in batches to respect rate limits."""
    resp = openai.Embedding.create(model=MODEL, input=texts)
    return [d["embedding"] for d in resp["data"]]

# gather markdown files
files = list(DATA_DIR.rglob("*.md"))
print(f"Found {len(files)} markdown files")

for i in tqdm(range(0, len(files), BATCH_SIZE), desc="Embedding"):
    batch_files = files[i:i+BATCH_SIZE]
    batch_texts = [f.read_text(encoding="utf-8")[:8000] for f in batch_files]
    embeddings = embed_batch(batch_texts)

    rows = []
    for f, emb in zip(batch_files, embeddings):
        rows.append({
            "content": f.read_text(encoding="utf-8"),
            "metadata": {"path": str(f)},
            "embedding": emb,
        })
    supabase.table("documents").insert(rows).execute()
    time.sleep(1)   # gentle pause to avoid bursts

print("✅ All documents ingested.")
