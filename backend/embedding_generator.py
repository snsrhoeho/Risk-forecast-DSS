# backend/embedding_generator.py
import os, sys
from pathlib import Path
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ROOT = Path(__file__).resolve().parents[1]

# ── CLI 인자 ──────────────────────────────────────────
if len(sys.argv) == 3:
    CSV_IN  = Path(sys.argv[1]).resolve()
    CSV_OUT = Path(sys.argv[2]).resolve()
else:
    CSV_IN  = ROOT / "data" / "raw" / "kosis_sample_template.csv"
    CSV_OUT = ROOT / "data" / "processed" / "embedded_output.csv"
CSV_OUT.parent.mkdir(parents=True, exist_ok=True)

print("📂 CSV 경로:", CSV_IN)
df = pd.read_csv(CSV_IN)

def embed(text: str):
    return client.embeddings.create(
        model="text-embedding-3-small",
        input=text, dimensions=1536
    ).data[0].embedding

df["embedding"] = df["text"].apply(embed)
df.to_csv(CSV_OUT, index=False)
print("✅ 임베딩 완료! →", CSV_OUT)
