import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

app = Flask(__name__)

API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not API_KEY:
            return jsonify({"error": "API key is missing. Check your .env file."}), 500

        data = request.get_json()
        message = data.get("message", "").strip()
        history = data.get("history", [])

        if not message:
            return jsonify({"error": "Please say something."}), 400

        messages = [
            {
                "role": "system",
                "content": "You are Consumer Voice AI, a friendly and helpful voice assistant. Answer clearly using simple English. Keep answers short and conversational."
            }
        ]

        for item in history[-10:]:
            if item.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": item["role"],
                    "content": str(item.get("content", ""))[:2000]
                })

        messages.append({
            "role": "user",
            "content": message
        })

        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-120b",
                "messages": messages,
                "temperature": 0.5,
                "max_completion_tokens": 500
            },
            timeout=60
        )

        if response.status_code != 200:
            return jsonify({"error": "AI service error: " + response.text[:300]}), 502

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        return jsonify({"answer": answer})

    except requests.exceptions.RequestException:
        return jsonify({"error": "Unable to connect to AI. Check your internet connection."}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
