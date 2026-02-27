# EchoMind — Real-Time Earnings Call & Media Intelligence Engine

## Elevator Pitch

Upload or stream an earnings call video and EchoMind produces a fully structured intelligence brief in under 2 minutes: who said what, extracted financial entities, voice confidence analysis, fact-checked claims, visual slide analysis, and an AI-generated executive summary.

**Demo vertical:** Financial earnings calls & investor podcasts.

---

## Prize Strategy

We target **5 sponsor prizes** simultaneously — all cash/gift card sponsors plus Render:

| Sponsor | Prize Pool | Type | Our Integration |
|---------|-----------|------|-----------------|
| **Render** | $1,000 | Credits | Deploy 4+ services (web, static, postgres, cron) |
| **Modulate** | $1,750 | Cash | Voice tone/confidence analysis on speakers |
| **Yutori** | $2,500 | Visa gift cards | Research API for fact-checking claims |
| **Fastino/GLiNER2** | $1,750 | Gift cards | Entity extraction + Pioneer fine-tuning |
| **Reka Vision** | $1,750 | Cash + interview | Video frame analysis (slides, charts, expressions) |

**Total potential: ~$7,750 in cash/gift cards** + Render credits + job interviews.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Render Platform                         │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Static Site  │  │ Web Service  │  │   Cron Job     │  │
│  │ (React)      │──│ (FastAPI)    │  │ (Monitor new   │  │
│  │ Dashboard    │  │ Backend API  │  │  earnings calls)│  │
│  └─────────────┘  └──────┬───────┘  └────────────────┘  │
│                          │                                │
│                   ┌──────┴───────┐                       │
│                   │  PostgreSQL   │                       │
│                   │  (Results DB) │                       │
│                   └──────────────┘                       │
└──────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼──┐  ┌─────▼─────┐  ┌──▼──────────┐
     │ Reka      │  │ Fastino   │  │ Yutori      │
     │ Vision    │  │ GLiNER2   │  │ Research    │
     │ API       │  │ API       │  │ API         │
     └───────────┘  └───────────┘  └─────────────┘
              │
     ┌────────▼──┐
     │ Modulate  │
     │ Voice     │
     │ API       │
     └───────────┘
```

---

## How Each Sponsor API Is Used

### 1. Reka Vision API — Visual Intelligence Layer
- **Input:** Video frames extracted from earnings call recordings
- **Analysis:**
  - Slide/chart detection and content extraction ("Q3 revenue chart shows...")
  - Speaker expression analysis (confidence, engagement)
  - Visual content summarization across the full video
- **Output:** Structured visual intelligence per video segment
- **Why judges care:** Enterprise use case (financial analysis), multimodal video understanding at scale

### 2. Modulate — Voice Analysis Layer
- **Input:** Audio stream from earnings call
- **Analysis:**
  - Speaker tone and prosody analysis
  - Confidence/stress indicators during Q&A segments
  - Emotional state tracking over time (when does the CEO get nervous?)
  - Speaker change detection
- **Output:** Voice confidence timeline, flagged segments
- **Why judges care:** Creative use beyond toxicity — financial voice intelligence

### 3. Fastino/GLiNER2 — Entity Extraction Layer
- **Input:** Transcript text from earnings call
- **Analysis:**
  - Named entity extraction (companies, people, products, financial figures)
  - Classification of statements (forward-looking, risk factor, commitment, metric)
  - Relationship extraction (Company → Revenue → $X)
- **Fine-tuning with Pioneer:**
  - Provide 10 annotated earnings call examples
  - Fine-tune GLiNER2 on financial entity types
  - Show F1 score improvement over base model
- **Output:** Structured entity list, classified statements, extraction graph
- **Why judges care:** Judges want extraction + fine-tuning demo. F1 score comparison is a judging criterion.

### 4. Yutori — Research & Fact-Checking Layer
- **Input:** Claims and entities extracted by Fastino
- **Analysis:**
  - Research API verifies financial claims ("We grew revenue 40% YoY" → check SEC filings, news)
  - Pull competitor data and market context
  - Enrich entity data with current information (stock price, recent news)
  - Scouting API monitors for new earnings calls on a schedule
- **Output:** Fact-check results with sources, enriched entity profiles
- **Why judges care:** Autonomous web research that goes beyond simple search

### 5. Render — Infrastructure Layer
- **Services used (4 = exceeds the 2+ requirement):**
  1. **Web Service** — FastAPI backend (Python)
  2. **Static Site** — React dashboard (Vite)
  3. **PostgreSQL** — Store analysis results, entities, reports
  4. **Cron Job** — Scheduled monitoring for new earnings calls
- **Infrastructure as code:** `render.yaml` defines the full stack
- **Why judges care:** Production-ready deployment using multiple service types

---

## Tech Stack

### Backend (Render Web Service)
- **Python 3.11 + FastAPI**
- **SQLAlchemy + Alembic** for database ORM/migrations
- **Celery or background tasks** for async processing pipeline
- **ffmpeg** for audio/video extraction

### Frontend (Render Static Site)
- **React 18 + Vite**
- **Tailwind CSS** for styling
- **Recharts** for voice confidence timeline visualization
- **React Query** for API data fetching

### Database (Render PostgreSQL)
- Tables: analyses, entities, fact_checks, voice_segments, visual_segments

### Cron (Render Cron Job)
- Python script that checks for new earnings calls via Yutori Scouting API

---

## Project Structure

```
echomind/
├── render.yaml                     # Render infrastructure-as-code
├── plan.md                         # This file
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Environment config
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLAlchemy setup
│   │   └── schemas.py              # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── analysis.py             # POST /analyze, GET /analysis/:id
│   │   └── health.py               # Health check endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Coordinates all analysis services
│   │   ├── reka_service.py         # Reka Vision API integration
│   │   ├── modulate_service.py     # Modulate voice analysis
│   │   ├── fastino_service.py      # GLiNER2 entity extraction
│   │   ├── yutori_service.py       # Yutori research/fact-checking
│   │   └── transcript_service.py   # Audio-to-text processing
│   └── utils/
│       ├── __init__.py
│       └── media.py                # Video/audio processing helpers
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/
│       │   └── client.js           # API client
│       ├── components/
│       │   ├── Upload.jsx          # File upload / URL input
│       │   ├── Dashboard.jsx       # Main results dashboard
│       │   ├── EntityList.jsx      # Extracted entities display
│       │   ├── VoiceTimeline.jsx   # Voice confidence over time
│       │   ├── VisualInsights.jsx  # Reka vision results
│       │   ├── FactChecks.jsx      # Yutori fact-check results
│       │   └── Summary.jsx         # Executive summary
│       └── styles/
│           └── index.css
│
└── cron/
    ├── Dockerfile
    ├── requirements.txt
    └── monitor.py                  # Scheduled earnings call monitor
```

---

## API Endpoints

### Backend API

```
POST /api/analyze
  - Body: { url: string } OR multipart file upload
  - Returns: { analysis_id: string, status: "processing" }

GET /api/analysis/{id}
  - Returns full analysis results (entities, voice, visual, fact-checks, summary)

GET /api/analysis/{id}/status
  - Returns processing status and progress

GET /api/analyses
  - Returns list of all analyses (paginated)

GET /api/health
  - Health check for Render
```

---

## Database Schema

```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY,
    title TEXT,
    source_url TEXT,
    status TEXT DEFAULT 'processing',  -- processing, completed, failed
    summary TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE entities (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES analyses(id),
    name TEXT,
    entity_type TEXT,       -- person, company, financial_figure, product, date
    context TEXT,           -- surrounding text
    confidence FLOAT
);

CREATE TABLE voice_segments (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES analyses(id),
    start_time FLOAT,
    end_time FLOAT,
    speaker TEXT,
    confidence_score FLOAT,
    tone TEXT,              -- confident, nervous, evasive, neutral
    transcript TEXT
);

CREATE TABLE visual_segments (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES analyses(id),
    timestamp FLOAT,
    frame_url TEXT,
    description TEXT,       -- Reka's description of what's on screen
    content_type TEXT       -- slide, chart, speaker, product_demo
);

CREATE TABLE fact_checks (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES analyses(id),
    claim TEXT,
    verdict TEXT,           -- verified, unverified, disputed, context_needed
    evidence TEXT,
    sources JSONB
);
```

---

## Demo Script (2 minutes)

1. **Open dashboard** — Clean UI, "EchoMind" branding
2. **Paste URL** — Drop in a real Apple/Tesla earnings call YouTube URL
3. **Show processing** — "Analyzing with 4 AI services simultaneously..."
4. **Results dashboard:**
   - **Executive Summary** — 3-paragraph AI brief
   - **Entity Panel** — Companies, people, figures extracted by Fastino
   - **Voice Timeline** — Confidence/stress graph from Modulate (highlight where CEO got nervous during margin question)
   - **Visual Insights** — Slides and charts detected by Reka ("Revenue slide at 14:23 shows...")
   - **Fact Checks** — Claims verified by Yutori with source links
5. **Punchline:** "What took a financial analyst 4 hours now takes 90 seconds. Built on Render, powered by Reka, Modulate, Fastino, and Yutori."

---

## Implementation Priority

1. **P0 (Must have for demo):**
   - Backend API skeleton on Render
   - Reka Vision integration (video analysis)
   - Fastino/GLiNER2 integration (entity extraction) + Pioneer fine-tuning
   - Basic frontend dashboard
   - render.yaml with all 4 services

2. **P1 (High impact):**
   - Yutori Research API (fact-checking)
   - Modulate voice analysis
   - Voice confidence timeline visualization

3. **P2 (Nice to have):**
   - Cron job for automated monitoring
   - Yutori Scouting API integration
   - Entity relationship graph visualization
   - Export to PDF report

---

## Environment Variables

```
# Reka
REKA_API_KEY=

# Modulate
MODULATE_API_KEY=

# Fastino
FASTINO_API_KEY=

# Yutori
YUTORI_API_KEY=

# Database
DATABASE_URL=  (provided by Render PostgreSQL)

# App
FRONTEND_URL=  (Render static site URL, for CORS)
```
