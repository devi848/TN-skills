# PocketSmart AI

PocketSmart AI is a smart budget and recommendation assistant.

The application provides:

- User registration
- User login
- Logout
- Dashboard
- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner
- Optional outfit image upload
- Gemini AI integration
- Local fallback recommendations
- Recommendation history
- Shopping search links
- SQLite database
- FastAPI backend
- Jinja2 frontend

---

# Project Structure

```text
PocketSmartAI/
│
├── app/
│   ├── __init__.py
│   ├── ai.py
│   ├── auth.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   ├── recommendations.py
│   └── schemas.py
│
├── data/
│   └── .gitkeep
│
├── uploads/
│   └── .gitkeep
│
├── static/
│   ├── app.js
│   └── styles.css
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── home_planner.html
│   ├── party_planner.html
│   ├── jewelry_planner.html
│   ├── recommendation.html
│   └── history.html
│
├── tests/
│   └── test_app.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md