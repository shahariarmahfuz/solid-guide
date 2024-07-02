import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import threading
import time
import requests

app = Flask(__name__)

# Get API key from Replit secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_sessions = {}  # Dictionary to store chat sessions per user

@app.route('/ask', methods=['GET'])
def ask():
    query = request.args.get('q')
    user_id = request.args.get('id')

    if not query or not user_id:
        return jsonify({"error": "Please provide both query and id parameters."}), 400

    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    chat_session = chat_sessions[user_id]
    response = chat_session.send_message(query)
    return jsonify({"response": response.text})

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive"})

def keep_alive():
    url = "https://gemini-5nx0.onrender.com/ping"  # আপনার রেন্ডার URL এখানে বসান
    while True:
        time.sleep(900)  # Ping every 5 minutes
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Ping successful")
            else:
                print("Ping failed with status code", response.status_code)
        except Exception as e:
            print("Ping failed with exception", e)

if __name__ == '__main__':
    # Start keep-alive thread
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
