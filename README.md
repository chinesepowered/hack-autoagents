# EchoMind

Real-Time Earnings Call & Media Intelligence Engine.

Upload or stream an earnings call video and EchoMind produces a structured intelligence brief: entity extraction, voice confidence analysis, visual slide analysis, fact-checked claims, and an executive summary.

## Quick Start

### Backend
```bash
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

### Deploy to Render
Connect this repo to Render and it will auto-deploy using `render.yaml`.

## Sponsor Integrations
- **Reka Vision** — Video frame analysis (slides, charts, expressions)
- **Modulate** — Voice tone/confidence analysis
- **Fastino/GLiNER2** — Entity extraction + Pioneer fine-tuning
- **Yutori** — Research API for fact-checking claims
- **Render** — 4-service deployment (web, static, postgres, cron)
