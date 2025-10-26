import os, json, math, requests
from pathlib import Path

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DATA_FILE = Path("data/knowledge.jsonl")

class SimpleRAG:
    def __init__(self, api_key: str, k: int = 3):
        self.api_key = api_key
        self.k = k
        self.docs = []
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        self.docs.append(json.loads(line))
                    except:
                        pass

    def _embed(self, texts):
        resp = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": EMBED_MODEL, "input": texts}
        ).json()
        return [d["embedding"] for d in resp["data"]]

    @staticmethod
    def _cos(a,b):
        num = sum(x*y for x,y in zip(a,b))
        da = math.sqrt(sum(x*x for x in a)); db = math.sqrt(sum(y*y for y in b))
        return 0.0 if da==0 or db==0 else num/(da*db)

    def retrieve_context(self, query: str) -> str:
        if not self.docs:
            return ""
        qv = self._embed([query])[0]
        doc_vecs = self._embed([d["text"] for d in self.docs])
        scored = sorted(
            [(self._cos(qv, dv), self.docs[i]) for i, dv in enumerate(doc_vecs)],
            key=lambda x: x[0], reverse=True
        )[:self.k]
        lines = []
        for score, d in scored:
            src = d.get("source","local")
            lines.append(f"- ({score:.2f}) {d['text']} [fuente: {src}]")
        return "\n".join(lines)
