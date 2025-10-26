# main.py
import os
import requests
from flask import Flask, send_from_directory, jsonify, request
from utils.guardrails import is_allowed
from utils.setup_rag import post_query

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/session")
def session():
    return generate_session()

def generate_session():
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
                "Você é um assistente telefônico que ajuda pessoas a entender "
                "quais benefícios sociais do governo de São Paulo elas podem ter acesso.\n"
                "Quando o usuário falar sua idade, situação financeira ou se está desempregado, "
                "você deve ENVIAR o texto para o endpoint `/analyze` antes de responder.\n"
                "Use a resposta retornada pelo servidor como base para sua fala final."
            )
        },
    )
    return jsonify(r.json())

@app.post("/analyze")
def analyze():
    text = request.json.get("text", "")

    # 1) GUARDRAIL
    if not is_allowed(text):
        return jsonify({"result": "Desculpe, não posso ajudar com esse tipo de conteúdo."})

    # 2) RAG
    benefits = post_query(text)

    if not benefits:
        return jsonify({"result": "Não encontrei benefícios correspondentes ainda. Pode me contar um pouco mais sobre sua situação?"})

    # 3) Mensagem resumida para o modelo falar ao usuário
    return jsonify({
        "result": f"Com base nas suas informações, você pode ter acesso aos seguintes benefícios:\n\n{benefits}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5093, debug=True)
