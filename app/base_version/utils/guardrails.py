# guardrails.py
import requests
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def is_allowed(text: str) -> bool:
    """Valida a mensagem usando a moderação da OpenAI."""
    resp = requests.post(
        "https://api.openai.com/v1/moderations",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model": "omni-moderation-latest", "input": text}
    ).json()

    return not resp["results"][0]["flagged"]
