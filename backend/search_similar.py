# backend/search_similar.py
import os, numpy as np, psycopg2, faiss, ast
from dotenv import load_dotenv

load_dotenv()
DB = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user"  : os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", 5432),
}

conn = psycopg2.connect(**DB)
cur  = conn.cursor()

# 최신 데이터 (예: 2024년)
cur.execute("SELECT id,title,text,embedding FROM embeddings WHERE grp='C'")
current = cur.fetchall()

# 과거 데이터 (예: 2020~2023년)
cur.execute("SELECT id,title,text,embedding FROM embeddings WHERE grp='P'")
past = cur.fetchall()

cur.close(); conn.close()

if not past or not current:
    print("데이터가 부족합니다."); exit()

# ✅ 문자열 → float 리스트로 변환
p_ids, p_titles, p_texts, p_vecs_raw = zip(*past)
p_vecs = [ast.literal_eval(v) for v in p_vecs_raw]  # 👈 요줄 추가

index = faiss.IndexFlatL2(1536)
index.add(np.asarray(p_vecs, dtype="float32"))

print("\n🔍 최신 뉴스 ↔ 과거 유사 Top-3\n")
for cid, ctitle, ctext, cvec_str in current:
    cvec = np.asarray([ast.literal_eval(cvec_str)], dtype="float32")  # 👈 이것도 문자열일 수 있음
    D,I = index.search(cvec, k=4)
    print(f"🆕 {ctitle}")
    for rank, idx in enumerate(I[0]):
        if rank == 0:  # 가장 가까운 과거 1위
            p_title = p_titles[idx][:80]
            print(f"  {rank+1}) {p_title}  (거리 {D[0][rank]:.4f})")
    print()
