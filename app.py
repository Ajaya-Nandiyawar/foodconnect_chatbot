from flask import Flask, request, jsonify, render_template
from deep_translator import GoogleTranslator
import openai
import os
from dotenv import load_dotenv
load_dotenv()
# -----------------------------


app = Flask(__name__)

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
# -----------------------------
# Utility: Translate to English
# -----------------------------
def translate_input(user_input):
    return GoogleTranslator(source='auto', target='en').translate(user_input)

# -----------------------------
# FAQ-Based Responses
# -----------------------------
faq_knowledge_base = {
    "how to donate": "To donate, go to the Donate section and fill in the form.",
    "how to request food": "Go to the Request Food tab and fill in your details.",
    "how to contact": "Reach us at support@foodconnect.org or via the Contact Us page.",
    "map not working": "Try refreshing your browser or checking your location permissions."
}

from difflib import get_close_matches

def match_faq(user_input):
    user_input = user_input.lower()
    matches = get_close_matches(user_input, faq_knowledge_base.keys(), n=1, cutoff=0.6)
    if matches:
        return faq_knowledge_base[matches[0]]
    return None

# -----------------------------
# Fallback: OpenAI GPT Response
# -----------------------------
def gpt_fallback(translated_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": translated_input}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# -----------------------------
# Main Chatbot Response Logic
# -----------------------------
def chatbot_response(user_input):
    translated_input = translate_input(user_input)
    lower_input = translated_input.lower()

    # Check FAQs
    faq_answer = match_faq(translated_input)
    if faq_answer:
        return faq_answer

    # Rule-based responses
    if "hello" in lower_input or "hi" in lower_input:
        return "Hi there! Welcome to FoodConnect. How can I assist you today?"
    elif "donate food" in lower_input:
        return "That's wonderful! You can donate food by clicking on the 'Donate' button and filling in the required details."
    elif "request food" in lower_input:
        return "To request food, please visit the 'Request Food' section and fill out your information. We'll match you with nearby donors."
    elif "track request" in lower_input:
        return "You can track your request status by logging into your dashboard and checking the 'My Requests' tab."
    elif "contact support" in lower_input or "help" in lower_input:
        return "You can reach out to our support team via the 'Contact Us' page or email us at support@foodconnect.org."
    elif "map not loading" in lower_input:
        return "Please ensure you have a stable internet connection. If the issue persists, try refreshing the page or checking browser permissions."
    elif "bye" in lower_input or "exit" in lower_input:
        return "Goodbye! Hope to see you again soon."

    # Fallback to GPT
    return gpt_fallback(translated_input)

# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    response = chatbot_response(user_input)
    return jsonify({"reply": response})

# -----------------------------
# Main Entrypoint
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
