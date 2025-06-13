# backend/insert_embeddings.py
import os, sys, time, ast
from pathlib import Path
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python insert_embeddings.py <embedded_csv> [group]")
    sys.exit(1)

CSV_PATH = Path(sys.argv[1]).resolve()
GROUP    = sys.argv[2] if len(sys.argv) > 2 else "P"
print("📂 CSV 경로:", CSV_PATH, "| grp:", GROUP)

DB = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user"  : os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", 5432),
}

# ── DB 연결 (재시도 10회) ─────────────────────────────
for i in range(10):
    try:
        conn = psycopg2.connect(**DB)
        break
    except psycopg2.OperationalError:
        print(f"⏳ DB 재시도({i+1}/10)")
        time.sleep(1)
else:
    raise RuntimeError("DB 연결 실패")

cur = conn.cursor()
cur.execute("""
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE IF NOT EXISTS embeddings (
        id  SERIAL PRIMARY KEY,
        title TEXT, text TEXT,
        embedding VECTOR(1536),
        grp CHAR(1) DEFAULT 'P'
    );
""")
conn.commit()
print("✅ pgvector & 테이블 준비 완료")

df = pd.read_csv(CSV_PATH)
df["embedding"] = df["embedding"].apply(ast.literal_eval)

for _, row in df.iterrows():
    cur.execute(
        "INSERT INTO embeddings (title,text,embedding,grp) VALUES (%s,%s,%s,%s)",
        (row["title"], row["text"], row["embedding"], GROUP)
    )
conn.commit()
cur.close(); conn.close()
print("✅ 모든 임베딩 데이터를 DB에 저장 완료!")
