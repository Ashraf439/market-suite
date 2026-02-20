from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
CORS(app)

# Load API key from environment variable for security
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def call_groq(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(GROQ_URL, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        result = data["choices"][0]["message"]["content"]

        # Clean markdown symbols
        result = re.sub(r"[*_`#]", "", result)
        return result
    except Exception as e:
        return f"API error: {str(e)}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate_campaign", methods=["POST"])
def generate_campaign():
    data = request.get_json()
    product = data.get("product")
    audience = data.get("audience")
    platform = data.get("platform")

    if not product or not audience or not platform:
        return jsonify({"error": "Missing required fields"}), 400

    prompt = (
        f"Generate a detailed marketing campaign.\n"
        f"Product: {product}\n"
        f"Target Audience: {audience}\n"
        f"Platform: {platform}\n"
        f"Include: Campaign strategy, key messages, and sample ad copy."
    )

    output = call_groq(prompt)
    return jsonify({"result": output})


@app.route("/generate_pitch", methods=["POST"])
def generate_pitch():
    data = request.get_json()
    product = data.get("product")
    customer = data.get("customer")

    if not product or not customer:
        return jsonify({"error": "Missing required fields"}), 400

    prompt = (
        f"Create a compelling AI sales pitch.\n"
        f"Product: {product}\n"
        f"Customer Persona: {customer}\n"
        f"Include: 30-second pitch, value proposition, and closing statement."
    )

    output = call_groq(prompt)
    return jsonify({"result": output})


@app.route("/lead_score", methods=["POST"])
def lead_score():
    data = request.get_json()
    name = data.get("name")
    budget = data.get("budget")
    need = data.get("need")
    urgency = data.get("urgency")

    if not name or not budget or not need or not urgency:
        return jsonify({"error": "Missing required fields"}), 400

    prompt = (
        f"Score this lead (0-100) based on Budget, Need, and Urgency.\n"
        f"Lead Name: {name}\n"
        f"Budget: {budget}\n"
        f"Need: {need}\n"
        f"Urgency: {urgency}\n"
        f"Provide a numeric score and a short explanation."
    )

    output = call_groq(prompt)
    return jsonify({"result": output})

@app.route("/campaign")
def campaign_page():
    return render_template("campaign.html")

@app.route("/pitch")
def pitch_page():
    return render_template("pitch.html")

@app.route("/lead")
def lead_page():
    return render_template("lead.html")

if __name__ == "__main__":
    app.run(debug=True)