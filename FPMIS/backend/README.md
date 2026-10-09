# FPMIS Backend

FastAPI backend application.

## Setup

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Run

```bash
python -m uvicorn app.main:app --reload --port 8000
```

## API Documentation

Visit http://localhost:8000/docs after starting the server.
