# Sponsor Integrations

How EchoMind leverages sponsor technologies to transform earnings calls into actionable intelligence.

---

## 🎤 Modulate — Voice Intelligence

**API:** Velma-2 Batch Transcription

We use Modulate's Velma-2 API to analyze the audio track of earnings calls with:
- **Speaker Diarization** — Identifies and separates different speakers (CEO, CFO, analysts)
- **Emotion Detection** — Detects emotional tone per utterance (confident, nervous, evasive)
- **Accent Identification** — Provides additional speaker context

This powers our "Voice Confidence Timeline" feature, letting users spot moments when executives sound less confident during tough Q&A.

---

## 👁️ Reka — Visual Intelligence

**API:** Reka Vision API

We use Reka's multimodal vision capabilities to analyze video frames extracted from earnings calls:
- **Slide Detection** — Identifies when presentation slides appear on screen
- **Chart Analysis** — Extracts data from financial charts and graphs
- **Text Extraction** — Reads on-screen text, numbers, and metrics
- **Speaker Expression** — Analyzes visual cues from speaker video feeds

This powers our "Visual Insights" panel with timestamped slide summaries like "Revenue slide at 14:23 shows 23% YoY growth."

---

## 🏷️ Fastino — Entity Extraction

**API:** GLiNER2 with Pioneer Fine-Tuning

We use Fastino's GLiNER2 model for structured entity extraction from earnings call transcripts:
- **Financial Entities** — Revenue figures, margins, growth percentages
- **Company & People** — Organizations mentioned, executive names
- **Forward-Looking Statements** — Guidance, projections, expectations
- **Risk Factors** — Disclosed risks and uncertainties

Pioneer fine-tuning improves extraction accuracy on financial domain terminology.

---

## 🔍 Yutori — Fact-Checking & Research

**API:** Yutori Research API

We use Yutori's autonomous research agents to verify claims made during earnings calls:
- **SEC Filing Verification** — Cross-references claims against 10-K, 10-Q filings
- **News Corroboration** — Checks claims against recent news coverage
- **Public Data Validation** — Verifies metrics against publicly available data

Each claim is tagged as Verified, Needs Context, Disputed, or Unverified with source links.

---

## ☁️ Render — Infrastructure

**Services:** Web Service, Static Site, PostgreSQL

We deploy our entire stack on Render using infrastructure-as-code (`render.yaml`):
- **Backend API** — FastAPI web service (Python native runtime)
- **Frontend Dashboard** — React + Vite static site
- **Database** — Managed PostgreSQL for storing analysis results

Single `render.yaml` deploys all 3 services with environment variables and service linking.

---

## Not Used

The following sponsor technologies were available but not integrated into EchoMind:

| Sponsor | Reason |
|---------|--------|
| **Neo4j** | Using PostgreSQL for relational storage; no graph relationships needed |
| **Tavily Search** | Yutori provides our research/fact-checking needs |
| **Airbyte** | No ETL/data integration pipelines required |
