# MarketAI Suite

A modern, AI-powered marketing and sales productivity application designed to generate marketing campaigns, sales pitches, lead scores, market analyses, and business insights instantly. The application is built using Flask, Groq API (Llama-3.3-70b-versatile model), and has a premium, responsive user interface.

## Features

- **User Authentication**: Simple and secure sign-up and sign-in functionality to keep your data personalized.
- **AI Marketing Campaigns**: Generate detailed marketing strategies, ad copy variations, and content ideas tailored to specific products, target audiences, and platforms.
- **AI Sales Pitches**: Create compelling, personalized elevator pitches and value propositions based on customer personas.
- **AI Lead Scoring**: Quantify lead qualification (0-100) using budget, need, and urgency inputs to predict the probability of conversion.
- **History Tracking**: Automatically saves all generated content (campaigns, pitches, leads, analyses, insights) to a user's personal history page with filtering by type.
- **Dashboard Analytics**: A clean, centralized dashboard showing generation statistics across all five tools.

## Technology Stack

- **Backend**: Python, Flask, Flask-CORS
- **AI Engine**: Groq API (`llama-3.3-70b-versatile` model)
- **Frontend**: HTML5, Vanilla CSS (designed with premium visual aesthetics), JavaScript (Fetch API)
- **Data Storage**: In-memory Python dictionaries for fast prototyping (designed to be easily replaced with an SQL/NoSQL database in production).

## Setup & Installation

1. **Navigate to your project directory**:
   ```bash
   cd market-suite
   ```

2. **Create a Virtual Environment** (Optional but highly recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure `flask`, `flask-cors`, and `requests` are installed. If `requirements.txt` is missing, you can manually install them via `pip install flask flask-cors requests`).*

4. **Environment Variables & Configuration**:
   The application reads `GROQ_API_KEY` and `SECRET_KEY` from environment variables, falling back to defaults defined in `app.py`. For production, set these as environment variables rather than relying on the hardcoded fallbacks.

5. **Run the Application**:
   ```bash
   python app.py
   ```
   The application will start in debug mode by default on `http://127.0.0.1:5000/`.

## Usage

1. **Register** a new account from the authentication portal.
2. **Log in** using your newly created credentials.
3. Access the suite's core tools through the navigation bar:
   - **Campaign Builder**: Generate complete, actionable marketing campaigns.
   - **Pitch Generator**: Create highly specific sales pitches based on your product and customer persona.
   - **Lead Scorer**: Evaluate incoming prospects based on budget, urgency, and need.
4. Review your past AI outputs easily in the **History** tab, with filters for each content type.

## Project Structure

```
market-suite/
├── app.py                  # Flask backend — routes and Groq API integration
├── requirements.txt
├── templates/
│   ├── base.html           # Shared layout and navbar
│   ├── index.html          # Dashboard with stats and feature cards
│   ├── campaign.html       # Campaign Generator
│   ├── pitch.html          # Sales Pitch Creator
│   ├── lead.html           # Lead Qualifier
│   ├── history.html        # History with type filters
│   ├── login.html
│   └── register.html
└── static/
    └── style.css
```

## Future Improvements

- Replace the in-memory data structures (`users` and `history_store`) with a fully-fledged database like PostgreSQL or SQLite.
- Move hardcoded secret keys (`SECRET_KEY`, `GROQ_API_KEY`) to a `.env` file for secure, environment-agnostic deployment.
- Implement rich-text exporting (e.g., downloading generated reports as PDF or Word documents).
- Add data visualizations (charts, graphs) to the Market Analysis and Business Insights pages.
