# FPMIS - Forensic Post-Mortem Intelligence System

A comprehensive digital platform for forensic post-mortem case management, developed by Digital Care Crew.

## Features

- **Case Management**: Create and manage forensic cases with complete tracking
- **Autopsy Reports**: Digital autopsy documentation with injury logging
- **Time of Death Calculator**: Scientific TOD estimation using multiple parameters
- **Decomposition Tracking**: Stage-wise decomposition logging with environmental factors
- **Evidence Management**: Chain of custody tracking for all evidence items
- **Missing Persons Matching**: Algorithmic matching between unidentified bodies and missing person reports
- **Pattern Detection**: Alert system for detecting suspicious patterns across cases

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+, SQLAlchemy
- **Database**: PostgreSQL 16

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 16

### Database Setup

```sql
CREATE DATABASE fpmis;
CREATE USER fpmis_user WITH PASSWORD 'fpmis_password';
GRANT ALL PRIVILEGES ON DATABASE fpmis TO fpmis_user;
```

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
FPMIS/
├── backend/
│   ├── app/
│   │   ├── models/       # Database models
│   │   ├── routers/      # API endpoints
│   │   └── schemas/      # Pydantic schemas
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   └── lib/              # Utilities
└── database/
    └── schema.sql        # Database schema
```

## Team

**Digital Care Crew**

## License

Proprietary - All Rights Reserved
