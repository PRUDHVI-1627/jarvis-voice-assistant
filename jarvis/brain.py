import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.2"

def think(user_text, history=None):
    if history is None:
        history = []

    history.append({"role": "user", "content": user_text})

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": history,
        "stream": False
    })

    reply = response.json()["message"]["content"]
    history.append({"role": "assistant", "content": reply})

    return reply, history