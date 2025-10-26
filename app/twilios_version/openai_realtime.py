import json, threading
import websocket

class RealtimeWS:
    def __init__(self, api_key, model, voice, session_update, on_event, on_close):
        self.api_key = api_key
        self.model = model
        self.voice = voice
        self.session_update = session_update
        self.on_event = on_event
        self.on_close_cb = on_close
        self.ws = None

    def start(self):
        url = f"wss://api.openai.com/v1/realtime?model={self.model}"
        headers = [
            f"Authorization: Bearer {self.api_key}",
            "OpenAI-Beta: realtime=v1"
        ]
        self.ws = websocket.WebSocketApp(
            url,
            header=headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=lambda *args: (self.on_close_cb() if self.on_close_cb else None),
            on_error=self._on_error
        )
        self.th = threading.Thread(target=lambda: self.ws.run_forever(origin="https://localhost"), daemon=True)
        self.th.start()

    def _on_open(self, ws):
        ws.send(json.dumps(self.session_update))

    def _on_message(self, ws, message):
        try:
            evt = json.loads(message)
        except Exception:
            return
        if self.on_event:
            self.on_event(evt)

    def _on_error(self, ws, err):
        pass

    def send(self, event: dict):
        if self.ws:
            self.ws.send(json.dumps(event))

    def close(self):
        try:
            if self.ws:
                self.ws.close()
        except:
            pass
