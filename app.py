from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import requests
import re
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'marketai-secret-key-change-in-production')
CORS(app)

# Groq Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Simple in-memory storage (replace with a DB in production)
users = {}
history_store = {}


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
        response = requests.post(GROQ_URL, json=body, headers=headers, timeout=30)
        data = response.json()
        result = data["choices"][0]["message"]["content"]
        # Clean asterisks and extra markdown
        result = re.sub(r'[\*\_]{1,3}(.*?)[\*\_]{1,3}', r'\1', result)
        return result
    except Exception as e:
        return f"API error: {str(e)}"


def save_history(user, item_type, title, result):
    if user not in history_store:
        history_store[user] = []
    history_store[user].insert(0, {
        'type': item_type,
        'title': title,
        'preview': result[:100] + '...' if len(result) > 100 else result,
        'result': result,
        'created_at': datetime.now().strftime('%b %d, %H:%M')
    })


# ── AUTH ROUTES ──────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if email in users and users[email]['password'] == password:
            session['user'] = users[email]['name']
            session['email'] = email
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not name or not email or not password:
            flash('All fields are required.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif email in users:
            flash('Email already registered.', 'error')
        else:
            users[email] = {'name': name, 'password': password}
            flash('Account created! Please sign in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── MAIN ROUTES ──────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session.get('email', '')
    items = history_store.get(email, [])
    stats = {
        'campaigns': sum(1 for i in items if i['type'] == 'campaign'),
        'pitches': sum(1 for i in items if i['type'] == 'pitch'),
        'leads': sum(1 for i in items if i['type'] == 'lead'),
    }
    return render_template('index.html', stats=stats)


@app.route('/campaign')
def campaign():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('campaign.html')


@app.route('/pitch')
def pitch():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('pitch.html')


@app.route('/lead')
def lead():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('lead.html')


@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session.get('email', '')
    items = history_store.get(email, [])
    return render_template('history.html', history=items)


# ── API ROUTES ───────────────────────────────────────────────────

@app.route('/generate_campaign', methods=['POST'])
def generate_campaign():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    product = request.form.get('product', '')
    audience = request.form.get('audience', '')
    platform = request.form.get('platform', '')
    prompt = (
        f"Generate a detailed marketing campaign strategy. "
        f"Product: {product}. Target Audience: {audience}. Platform: {platform}. "
        f"Include: Campaign Objectives, 5 Content Ideas, 3 Ad Copy Variations, "
        f"CTA Suggestions, and Tracking & Measurement tips. Be specific and actionable."
    )
    result = call_groq(prompt)
    save_history(session.get('email', ''), 'campaign', f"Campaign for {product}", result)
    return jsonify({'result': result})


@app.route('/generate_pitch', methods=['POST'])
def generate_pitch():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    product = request.form.get('product', '')
    customer = request.form.get('customer', '')
    prompt = (
        f"Create a compelling AI sales pitch. Product: {product}. "
        f"Customer Persona: {customer}. "
        f"Include: 30-second elevator pitch, Value Proposition, Key Differentiators, "
        f"and a strategic Call-to-Action. Make it persuasive and specific."
    )
    result = call_groq(prompt)
    save_history(session.get('email', ''), 'pitch', f"Pitch for {product}", result)
    return jsonify({'result': result})


@app.route('/lead_score', methods=['POST'])
def lead_score():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    name = request.form.get('name', '')
    budget = request.form.get('budget', '')
    need = request.form.get('need', '')
    urgency = request.form.get('urgency', '')
    prompt = (
        f"Score this lead (0-100) based on Budget, Need, and Urgency. "
        f"Lead Name: {name}. Budget: {budget}. Need: {need}. Urgency: {urgency}. "
        f"Provide: Lead Qualification Score (numeric), detailed Scoring Reasoning "
        f"(breakdown by Budget/Need/Urgency), and Probability of Conversion (%)."
    )
    result = call_groq(prompt)
    save_history(session.get('email', ''), 'lead', f"Lead Score: {name}", result)
    return jsonify({'result': result})


if __name__ == '__main__':
    app.run(debug=True)