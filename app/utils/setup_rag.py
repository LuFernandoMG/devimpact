import httpx
import json

URL_MCP_RAG = "http-url"

def post_query(self, query: str) -> httpx.Response:
    url = URL_MCP_RAG
    
    try:
        body = {"query": query}
        headers = {"Content-Type": "application/json"}
        response = httpx.post(url, json=body, headers=headers)
    
    except httpx.HTTPError as e:
        print(f"An error occurred while making the request: {e}")
        return None
    
    return json.loads(response.text).get("message", None)