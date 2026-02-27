# 🎙️ EchoMind

### Real-Time Earnings Call & Media Intelligence Engine

> 💡 What took a financial analyst **4 hours** now takes **90 seconds**.

Upload any earnings call video and EchoMind produces a fully structured intelligence brief — who said what, extracted financial entities, speaker confidence analysis, fact-checked claims with sources, visual slide analysis, and an AI-generated executive summary.

---

## 🚀 What It Does

EchoMind transforms raw earnings call recordings into actionable intelligence by running **4 AI analysis services in parallel**:

| Layer | What It Does |
|-------|-------------|
| 👁️ **Visual Intelligence** | Analyzes video frames — detects slides, charts, speaker expressions, and extracts on-screen data using **Reka Vision API** |
| 🎤 **Voice Analysis** | Tracks speaker confidence, stress indicators, and emotional tone throughout the call using **Modulate** |
| 🏷️ **Entity Extraction** | Pulls structured entities — people, companies, financial figures, forward-looking statements, risk factors — using **Fastino/GLiNER2** with Pioneer fine-tuning |
| ✅ **Fact-Checking** | Verifies claims against SEC filings, news, and public data in real-time using **Yutori Research API** |

---

## 🎯 The Problem

Financial analysts spend **3-5 hours per earnings call** manually:
- Transcribing and reading through hour-long calls
- Extracting key metrics and forward-looking statements
- Cross-referencing claims against public filings
- Summarizing findings for investment committees

**EchoMind automates the entire workflow.**

---

## 🖥️ Demo

**Input:** Paste a YouTube URL of any public earnings call

**Output:**
- 📊 **Executive Summary** — 3-paragraph AI brief with key takeaways
- 🏷️ **Entity Panel** — Companies, people, financial figures, risk factors extracted and categorized
- 📈 **Voice Confidence Timeline** — Interactive chart showing speaker confidence over time (spot when the CEO gets nervous during the margin question!)
- 👁️ **Visual Insights** — Slides and charts detected with content extracted ("Revenue slide at 14:23 shows 23% YoY growth")
- ✅ **Fact Checks** — Each major claim tagged as Verified, Needs Context, Disputed, or Unverified with sources

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Render Platform                           │
│                                                               │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────────┐ │
│  │ Static Site   │  │  Web Service  │  │    Cron Job       │ │
│  │ React + Vite  │──│  FastAPI      │  │ Earnings Monitor  │ │
│  │ Dashboard     │  │  Backend API  │  │ (Yutori Scouting) │ │
│  └──────────────┘  └───────┬───────┘  └───────────────────┘ │
│                            │                                  │
│                     ┌──────┴───────┐                         │
│                     │  PostgreSQL   │                         │
│                     │  Results DB   │                         │
│                     └──────────────┘                         │
└──────────────────────────────────────────────────────────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
      ┌────────▼───┐  ┌─────▼──────┐  ┌──▼──────────┐
      │ Reka       │  │ Fastino    │  │ Yutori      │
      │ Vision API │  │ GLiNER2    │  │ Research    │
      └────────────┘  └────────────┘  └─────────────┘
               │
      ┌────────▼───┐
      │ Modulate   │
      │ Voice API  │
      └────────────┘
```

**4 Render services:** Web Service + Static Site + PostgreSQL + Cron Job

---

## ⚡ Quick Start

### Backend
```bash
cp .env.example .env
# Add your API keys to .env

cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### 🚢 Deploy to Render
Connect this repo and Render auto-deploys all 4 services using `render.yaml` — infrastructure as code.

---

## 🔧 Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React 18, Vite, Tailwind CSS, Recharts
- **AI Services:** Reka Vision, Modulate, Fastino/GLiNER2, Yutori
- **Infrastructure:** Render (Web Service, Static Site, PostgreSQL, Cron Job)
- **Media Processing:** yt-dlp, ffmpeg

---

## 📂 Project Structure

```
├── render.yaml              # Render infrastructure-as-code (4 services)
├── backend/
│   ├── main.py              # FastAPI application
│   ├── services/
│   │   ├── orchestrator.py  # Parallel analysis pipeline
│   │   ├── reka_service.py  # Visual intelligence
│   │   ├── modulate_service.py  # Voice analysis
│   │   ├── fastino_service.py   # Entity extraction
│   │   └── yutori_service.py    # Fact-checking
│   ├── models/              # SQLAlchemy + Pydantic schemas
│   └── routers/             # API endpoints
├── frontend/
│   └── src/components/      # React dashboard components
└── cron/
    └── monitor.py           # Scheduled earnings call discovery
```

---

## 🔑 API Integrations

### Reka Vision API 👁️
Multimodal video/image understanding — analyzes video frames for slides, charts, speaker expressions. Enterprise-grade visual AI for financial content analysis.

### Modulate 🎤
Voice intelligence — analyzes speaker tone, prosody, and confidence. Goes beyond speech-to-text to understand *how* things are said. Detects when executives sound evasive during tough Q&A.

### Fastino/GLiNER2 🏷️
Fast, structured entity extraction with a 205M-parameter model. Extracts financial entities (companies, metrics, forward-looking statements, risk factors) and classifies statement types. Fine-tuned on financial data using Pioneer for improved F1 scores.

### Yutori 🔍
Autonomous web research agents — verifies financial claims against SEC filings, news, and public data. Scouting API monitors for new earnings calls on a schedule.

### Render ☁️
Modern PaaS powering the full stack — 4 service types deployed via infrastructure-as-code (`render.yaml`). Web service, static site, managed PostgreSQL, and cron job for automated monitoring.
