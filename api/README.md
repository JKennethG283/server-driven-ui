# FastAPI backend

Live JSON store and avatar generation API for the Astrana SDUI frontend.

When `VITE_API_URL` points at this server, the web app loads users and matches from here instead of bundled JSON files. Avatar regeneration updates the store and the UI picks up changes via polling.

UI design generation is stored separately from the base user profile. The frontend can keep calling `GET /users/{id}`; the API merges the generated UI design into that existing user envelope.

## Setup

```bash
# from repo root
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r api/requirements.txt

copy api\.env.example api\.env
# For avatar generation, reuse tools/avatar_gen keys (or copy that .env)
```

## Run

```bash
# from repo root (PYTHONPATH must include repo root)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for interactive API docs.

## Deploy (Railway)

Repo includes a root `Dockerfile` and `railway.toml` (Docker builder) so Railway deploys the **API only**, not the `app/` frontend.

1. New Project → Deploy from GitHub → this repo (root directory empty).
2. Variables: `GOOGLE_API_KEY`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`.
3. Generate a public domain → test `/health`.

Railway should auto-detect the `Dockerfile`. If build fails, confirm **Settings → Builder** is Dockerfile, not Nixpacks.

## Connect the frontend

```bash
cd app
copy .env.example .env
# VITE_API_URL=http://localhost:8000
npm run dev
```

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/users` | List user summaries |
| `GET` | `/users/{id}` | Get user (`{ code, message, data }` envelope) |
| `PATCH` | `/users/{id}` | Update profile fields (`bio`, location, etc.) |
| `POST` | `/users/import` | Import/upload a profile JSON |
| `GET` | `/users/{id}/matches` | Match list for a user |
| `POST` | `/users/{id}/ui/generate` | Generate UI design JSON from a character profile |
| `POST` | `/users/{id}/avatar/generate` | Run avatar pipeline (background job) |

On first start, users are seeded from `app/src/data/profiles/*.json` into `api/data/users/` if the store is empty.

## Avatar generation

`POST /users/{id}/avatar/generate` sets `avatar_status` to `generating`, runs the same LangGraph pipeline as `tools/avatar_gen/generate.py` in a background task, then writes the updated user JSON. The frontend polls every 3s while status is `generating`.

Requires `GOOGLE_API_KEY`, `CLOUDFLARE_ACCOUNT_ID`, and `CLOUDFLARE_API_TOKEN` (see `tools/avatar_gen/.env.example`).

## UI design generation

`POST /users/{id}/ui/generate` accepts an updated `character_profile` and writes generated UI design fields to `api/data/ui_designs/{id}.json`. The generated design currently uses deterministic rules so it can be tested without an AI key. Personality traits drive the palette first, with zodiac element as a fallback.

`GET /users/{id}` composes the base user JSON with the saved UI design JSON before returning the normal `{ code, message, data }` envelope. This keeps the frontend fetch path unchanged while allowing UI style to be generated from character data.

## Example

```bash
curl http://localhost:8000/users/4
curl -X POST http://localhost:8000/users/4/ui/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"character_profile\":{\"zodiac\":{\"sign\":\"Rat\",\"element\":\"Water\",\"personality_traits\":[\"calm\",\"patient\"]},\"horoscope\":{\"sign\":\"Cancer\",\"personality_traits\":[\"nurturing\",\"intuitive\"]}}}"
curl -X POST http://localhost:8000/users/4/avatar/generate
```
