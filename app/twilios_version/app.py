# app.py
import os, json, base64, threading, queue, time
from flask import Flask, request, Response
from flask_sock import Sock
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream, Say
from openai_realtime import RealtimeWS
from guardrails import moderate_text
from rag import SimpleRAG

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REALTIME_MODEL = os.getenv("REALTIME_MODEL", "gpt-4o-mini-realtime-preview")
REALTIME_VOICE = os.getenv("REALTIME_VOICE", "alloy")
LANGUAGE = os.getenv("LANGUAGE", "es")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Você é um assistente telefônico que ajuda pessoas a entender quais benefícios sociais do governo de São Paulo elas podem ter acesso. Quando o usuário falar sua idade, situação financeira ou se está desempregado, você deve ENVIAR o texto para o endpoint `/analyze` antes de responder. Use a resposta retornada pelo servidor como base para sua fala final. Responde em Português.")
TOP_K = int(os.getenv("RAG_TOP_K", "3"))

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY pendente")

app = Flask(__name__)
sock = Sock(app)

# Configure CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

rag = SimpleRAG(OPENAI_API_KEY, k=TOP_K)  # Load knowledge base for this version

@app.get("/")
def index():
    return {"status": "ok", "endpoints": ["/health", "/incoming-call", "/twilio-media"]}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/incoming-call")
def incoming_call():
    """
    Twilio POST → retornamos TwiML que:
    - saluda
    - conecta o stream ao wss://{host}/twilio-media
    """
    host = request.headers.get("Host")
    scheme = "https" if request.is_secure else "https"  # We assume the TLS later
    ws_url = f"wss://{host}/twilio-media"

    vr = VoiceResponse()
    vr.say("Num momento vamos-te ajudar", voice="Polly.Miguel")
    connect = Connect()
    connect.stream(url=ws_url)
    vr.append(connect)
    return Response(str(vr), mimetype="text/xml")

@sock.route("/twilio-media")
def twilio_media(ws):
    """
    WebSocket bidirecional com Twilio Media Streams.
    A Twilio envia mensagens JSON: start, media, mark, dtmf, stop. :contentReference[oaicite:5]{index=5}
    """
    to_twilio = queue.Queue()
    last_user_utterance = {"text": "", "item_id": None}
    stream_sid = None
    closed = threading.Event()

    # 1) Start Realtime
    oai = RealtimeWS(
        api_key=OPENAI_API_KEY,
        model=REALTIME_MODEL,
        voice=REALTIME_VOICE,
        # audio/pcmu == g711 μ-law 8 kHz, compatible con Twilio Media Streams. :contentReference[oaicite:6]{index=6}
        session_update={
            "type": "session.update",
            "session": {
                "type": "realtime",
                "model": REALTIME_MODEL,
                "instructions": SYSTEM_PROMPT,
                "output_modalities": ["audio"],
                "audio": {
                    "input": {
                        "format": {"type": "audio/pcmu"},
                        "turn_detection": {
                            "type": "server_vad",
                            "create_response": False,   
                            "silence_duration_ms": 700
                        }
                    },
                    "output": {
                        "format": {"type": "audio/pcmu"},
                        "voice": REALTIME_VOICE
                    }
                },
                "input_audio_transcription": {"language": LANGUAGE}
            }
        },
        on_event=lambda evt: handle_openai_event(evt, to_twilio, ws, last_user_utterance, oai, rag),
        on_close=lambda: closed.set()
    )
    oai.start()

    # 2) Thread: Reads Twilio and submit to OpenAI
    def twilio_reader():
        nonlocal stream_sid
        try:
            while True:
                raw = ws.receive()
                if raw is None:
                    break
                msg = json.loads(raw)
                et = msg.get("event")
                if et == "start":
                    stream_sid = msg["start"]["streamSid"]
                elif et == "media":
                    # Enviamos tal cual el payload base64 μ-law
                    oai.send({"type": "input_audio_buffer.append", "audio": msg["media"]["payload"]})
                elif et == "stop":
                    break
        finally:
            try:
                oai.close()
            except:
                pass
            closed.set()

    # 3) Thread: Takes OpenAI's audio and submit it to Twilio
    def twilio_writer():
        try:
            while not closed.is_set():
                try:
                    evt = to_twilio.get(timeout=0.1)
                except queue.Empty:
                    continue
                if evt["type"] == "response.output_audio.delta" and evt.get("delta") and stream_sid:
                    ws.send(json.dumps({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": evt["delta"]}
                    }))
        except Exception as e:
            closed.set()

    r = threading.Thread(target=twilio_reader, daemon=True)
    w = threading.Thread(target=twilio_writer, daemon=True)
    r.start(); w.start()
    while not closed.is_set():
        time.sleep(0.05)

def handle_openai_event(evt, to_twilio, ws, last_user_utterance, oai: "RealtimeWS", rag: "SimpleRAG"):
    """
    Roteador de eventos da API Realtime:
        - Reencaminha o áudio delta para a Twilio
        - Quando a transcrição do usuário chega, aplica moderação + RAG e cria a resposta
    """
    t = evt.get("type")

    if t == "response.output_audio.delta":
        to_twilio.put(evt)

    if t == "conversation.item.input_audio_transcription.completed":
        transcript = (evt.get("transcript")
                      or evt.get("item", {}).get("content", [{}])[0].get("transcript")
                      or "").strip()
        if not transcript:
            return
        last_user_utterance["text"] = transcript
        last_user_utterance["item_id"] = evt.get("item", {}).get("id")

        # 1) Guardrail
        mod = moderate_text(transcript)
        if mod.get("flagged"):
            oai.send({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "system",
                    "content": [{
                        "type": "input_text",
                        "text": "A última solicitação do usuário foi moderada. Responda com uma advertência gentil e ofereça ajuda segura."
                    }]
                }
            })
            oai.send({"type": "response.create"})
            return

        # 2) RAG: 
        ctx = rag.retrieve_context(transcript)
        if ctx:
            oai.send({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "system",
                    "content": [{
                        "type": "input_text",
                        "text": (
                            "Contexto recuperado (RAG). Use-o se for relevante, "
                            "e cite as fontes, se for o caso. Evite inventar:\n" + ctx
                        )
                    }]
                }
            })
        oai.send({"type": "response.create"})
