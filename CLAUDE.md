# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**Tsuburaya Intelligence Brief** (repo name: `kessho-lens`) — an AI-powered intelligence platform that monitors external news / regulation / tech trends across 7 categories and translates them into business implications for Tsuburaya Productions. News becomes **IntelCards** (fact + interpretation + insight + actions, importance A–D), which roll up into **Daily Briefs** emailed to executives, with 6 AI expert personas debating key topics in **Council Sessions**.

The README, docs, code comments, and all user-facing content are in **Japanese** — follow that convention when editing.

## Commands

### Backend (FastAPI, Python 3.11)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000     # API at :8000, OpenAPI docs at /docs
```

### Frontend (Next.js 14 App Router, TypeScript, Tailwind)
```bash
cd frontend
npm install
npm run dev      # http://localhost:3000 → redirects to /intel
npm run build
npm run lint     # next lint (only linter in the repo)
```

There is **no test suite** in either half of the repo. There is no Python linter/formatter config.

### Environment
Copy `.env.example` → `.env` at the repo root (backend loads it via `python-dotenv`). Everything degrades gracefully: without `ANTHROPIC_API_KEY` the generators fall back to template/rule-based output; Notion and email modules are no-ops unless their env vars are set (each module exposes `is_enabled()`).

### Manually trigger the daily pipeline
```bash
curl -X POST http://localhost:8000/api/intel/cron/daily-brief \
  -H "Authorization: Bearer $CRON_SECRET"
curl http://localhost:8000/api/intel/cron/status   # poll: running / done / skipped / error
```

## Architecture

Monorepo with four parts: `frontend/`, `backend/`, `shared/` (type definitions), `data/` (JSON storage at repo root).

### Daily pipeline (the core flow)

```
GitHub Actions cron (22:00 UTC = 07:00 JST, primary scheduler)
  → POST /api/intel/cron/daily-brief  (Bearer CRON_SECRET)
    → background task in backend/api/intel.py:_run_daily_brief_pipeline
      news_ingest.py   Google News RSS (no API key) → dedupe → card_generator
      card_generator.py  news → IntelCard via Claude API (template fallback)
      brief_generator.py IntelCards for the day → Daily Brief
      email_sender.py    Brief → HTML email via Resend API
      notion_sync.py     cards + briefs upserted to Notion DBs
```

- `.github/workflows/daily-brief.yml` is the **primary** scheduler (warms Render, triggers, polls `/api/intel/cron/status`). Vercel Cron (`vercel.json` → `frontend/app/api/cron/daily-brief/route.ts`) is a redundant backup that forwards to the same backend endpoint.
- **Spend guard**: the cron endpoint enforces `DAILY_BRIEF_MAX_RUNS_PER_DAY` (default 5) per 24h to cap Claude API cost; the "refresh now" button (`frontend/app/api/intel/refresh-today/route.ts`) goes through the same endpoint and limit.
- The cron endpoint returns 202 immediately and runs the pipeline via `BackgroundTasks`; callers poll `/api/intel/cron/status`.

### Storage and persistence

- All data is JSON files in `data/` (`intel_cards.json`, `intel_briefs.json`, `intel_council.json`, `intel_watchlist.json`), read/written through `backend/src/data/storage.py` with per-file locks and atomic writes (temp → rename). A future DB migration only needs to replace this module.
- **Render's disk is ephemeral**: Notion is the durable store. On startup (`backend/main.py`), cards and briefs are restored from Notion into local JSON. `notion_sync.py` stores the full card JSON in a Notion property for lossless round-trip.

### Domain definitions live in two backend modules

- `backend/src/intel/categories.py` — the 7 intel categories with labels, colors, watch targets, and responsible experts.
- `backend/src/intel/experts.py` — the 6 AI Council expert personas (system prompts, key questions) plus importance labels A–D.

Generators (`card_generator`, `council`) build Claude prompts from these; adding a category or expert means updating these files **and** the mirrored TypeScript types (see below).

### Type definitions are triplicated — keep them in sync

`shared/types.ts`, `shared/schemas.py` (Pydantic), and `frontend/lib/intel-types.ts` all define IntelCard/Brief/Council shapes. The frontend imports from `lib/intel-types.ts` (not `shared/`). Changing a data shape means touching all three.

### Frontend structure

- Pages under `frontend/app/intel/` (dashboard, cards, brief/[date], council, themes, kpi, agenda, actions, watchlist, notion, delivery). `frontend/app/api/` holds server-side proxy routes that keep `CRON_SECRET` off the browser.
- `lib/intel-api.ts` is the typed API client. `lib/api.ts:warmupBackend()` polls `/api/health` for up to ~70s because Render free tier cold-starts take ~50s — pages call it before fetching, and `intel-api.ts` retries 5xx responses. Keep this cold-start tolerance in mind for any new fetch logic.
- The "reform" layer (`lib/reform-types.ts`, `reform-taxonomies.ts`, `impact-score.ts`, `reform-mock.ts`) is a **frontend-only sidecar** over IntelCard: rule-based management-impact scoring (0–100 across 8 axes), theme/IP-lens classification via keyword regexes, KPIs, and weekly agenda. It deliberately does not extend IntelCard or touch the backend; `impact-score.ts` is pure functions designed to be swapped for LLM scoring later.

### Deployment

- Frontend → Vercel (root directory `frontend`), backend → Render (`render.yaml` blueprint, root `backend`). CORS in `backend/main.py` allows localhost plus `FRONTEND_URL`/`ALLOWED_ORIGINS` env vars and a regex for vercel/netlify/railway/onrender domains.
- `API_BASE` in the frontend falls back to the production Render URL when `NEXT_PUBLIC_API_BASE_URL` is unset.
- Deploy guide (Japanese): `docs/DEPLOY_JA.md`.
