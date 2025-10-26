import httpx
import json

URL_MCP_RAG = "https://n8n-887769016479.us-central1.run.app/webhook/perguntar-rag"

def post_query(self, query: str) -> httpx.Response:
    url = URL_MCP_RAG
    
    try:
        body = {"query": query}
        print(body)
        headers = {"Content-Type": "application/json"}
        response = httpx.post(url, json=body, headers=headers)
        print(response)
    
    except httpx.HTTPError as e:
        print(f"An error occurred while making the request: {e}")
        return None
    
    return json.loads(response.text).get("message", None)