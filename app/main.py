# main.py
import os
import requests
from flask import Flask, send_from_directory, jsonify

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder="static")

print("OpenAI API Key:", OPENAI_API_KEY)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/session")
def session():
    """Crea una sesión temporal Realtime para el navegador."""
    r = requests.post(
        "https://api.openai.com/v1/realtime/sessions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-realtime-preview",
            "voice": "verse",
            "instructions": (
                ""
            )
        },
    )
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5093, debug=True)
