# Phase 2 — Web Dashboard & Project Workflow

## Delivered

- React + TypeScript + Vite web application
- Login/register UI
- API client with JWT token handling
- Dashboard
- Dynamic project creation
- Source/transcript input
- Channel selector
- Content-profile selector
- Dynamic short/long video selection
- Dynamic duration and quantity
- Project list
- Channel/profile overview
- Responsive UI
- Backend CORS configuration
- Project API with tenant-owned reference validation
- Backend tests for project creation and tenant isolation

## Deliberately not included

- Real AI generation
- GPU workers
- YouTube OAuth
- Instagram OAuth
- actual video rendering
- TTS
- production job queue
- production secrets management

Those belong to later phases.

## Run

Backend:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:
```bash
cd web
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` unless `VITE_API_URL` is set.
