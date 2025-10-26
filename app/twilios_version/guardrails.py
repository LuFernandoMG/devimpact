import os, requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def moderate_text(text: str) -> dict:
    try:
        resp = requests.post(
            "https://api.openai.com/v1/moderations",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": "omni-moderation-latest", "input": text}
        ).json()
        r = resp.get("results", [{}])[0]
        return {"flagged": bool(r.get("flagged")), "categories": r.get("categories", {})}
    except Exception:
        return {"flagged": False}