# AI Content Factory — Phase 1

Phase 1 establishes the backend foundation.

## Included

- FastAPI application
- Pydantic settings
- SQLAlchemy 2.x ORM
- Alembic migrations
- SQLite development mode
- PostgreSQL production configuration
- Multi-tenant organization/user foundation
- Channel and platform-account entities
- Dynamic content profiles
- Content sources
- Projects and generation jobs
- AI model registry
- AI provider interfaces
- Storage abstraction with local backend and Google Cloud Storage adapter
- Password hashing + JWT access-token foundation
- Health endpoint
- API tests

## Run locally

### 1. Create environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
```

### 2. Install

```bash
pip install -e ".[dev]"
```

### 3. Configure

Copy `.env.example` to `.env` and set `SECRET_KEY`.

SQLite is used by default for development.

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start API

```bash
uvicorn app.main:app --reload
```

Open `/docs`.

### 6. Tests

```bash
pytest
```

## Production direction

Use PostgreSQL, a managed Redis/queue, Google Cloud Storage, and separate GPU workers. Do not run heavy AI inference inside the FastAPI process.


## Phase 48
Dynamic video provider/model selection added. See docs/PHASE_48.md.


## Phase 49
Dynamic TTS provider/model selection added. See docs/PHASE_49.md.


## Phase 50
Audio/video synchronization quality gate added. See docs/PHASE_50.md.


## Phase 51
Automatic media repair planner and execution boundary added. See docs/PHASE_51.md.


## Phase 52
FFmpeg media processing engine added. See docs/PHASE_52.md.


## Phase 53
End-to-end media repair orchestration added. See docs/PHASE_53.md.


## Phase 54
Production final render manifest and FFmpeg assembly layer added. See docs/PHASE_54.md.


## Phase 55
Voice-over and background music mixing layer added. See docs/PHASE_55.md.


## Phase 56
Dynamic subtitle/caption generation and optional FFmpeg burn-in added. See docs/PHASE_56.md.


## Phase 57
Speech-to-Text provider abstraction and word-timestamp contract added. See docs/PHASE_57.md.


## Phase 58
Real local faster-whisper Speech-to-Text provider and dynamic factory added. See docs/PHASE_58.md.


## Phase 59
STT-to-caption integration added. See docs/PHASE_59.md.


## Phase 60
Provider-neutral visual generation layer added.


## Phase 61
Scene-plan to visual-generation integration added.


## Phase 62
Visual asset quality gate and retry signal added.


## Phase 63
Final visual production orchestration and manual-review gate added.


## Phase 64
Final release manifest and core production handoff boundary added. Core phase series complete.

## Git-ready final build

This is the merged core project through Phase 64. Extract the `AI_Content_Factory` folder and use it as the Git repository.
