from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # In production, use os.urandom(24) or env var
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CORS(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    histories = db.relationship('History', backref='user', lazy=True)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tool = db.Column(db.String(50), nullable=False)
    prompt_data = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

GROQ_API_KEY = ""
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

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))
        
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/generate_campaign", methods=["POST"])
@login_required
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
    
    # Save to history
    new_history = History(
        user_id=current_user.id,
        tool='campaign',
        prompt_data=json.dumps({"product": product, "audience": audience, "platform": platform}),
        result=output
    )
    db.session.add(new_history)
    db.session.commit()
    
    return jsonify({"result": output})


@app.route("/generate_pitch", methods=["POST"])
@login_required
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
    
    # Save to history
    new_history = History(
        user_id=current_user.id,
        tool='pitch',
        prompt_data=json.dumps({"product": product, "customer": customer}),
        result=output
    )
    db.session.add(new_history)
    db.session.commit()
    
    return jsonify({"result": output})


@app.route("/lead_score", methods=["POST"])
@login_required
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
    
    # Save to history
    new_history = History(
        user_id=current_user.id,
        tool='lead_score',
        prompt_data=json.dumps({"name": name, "budget": budget, "need": need, "urgency": urgency}),
        result=output
    )
    db.session.add(new_history)
    db.session.commit()
    
    return jsonify({"result": output})

@app.route("/campaign")
@login_required
def campaign_page():
    return render_template("campaign.html")

@app.route("/pitch")
@login_required
def pitch_page():
    return render_template("pitch.html")

@app.route("/lead")
@login_required
def lead_page():
    return render_template("lead.html")

@app.route("/history")
@login_required
def history_page():
    user_history = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).all()
    
    # Parse prompt_data back to dictionaries for the template
    for item in user_history:
        item.parsed_data = json.loads(item.prompt_data)
        
    return render_template("history.html", history=user_history)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)