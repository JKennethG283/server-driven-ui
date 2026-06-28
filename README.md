# Server Driven UI

A TypeScript social app prototype where each user profile drives the entire UI — colors, typography, motion, and avatar backdrop — from a single JSON document. Includes a Python avatar generator that fills in mascot images and visual identity using Gemini and Cloudflare Workers AI.

**Live demo:** [https://server-driven-ui-fawn.vercel.app/](https://server-driven-ui-fawn.vercel.app/) — deployed on Vercel from the `app/` directory (Vite preset).

## What it does

- **Frontend (`app/`)** — React + Vite app themed per user via SDUI. Load bundled profiles or upload any schema-valid JSON; the app derives CSS variables from profile data and reskins instantly.
- **API (`api/`)** — FastAPI service: live user JSON store, matches, UI design generation, and avatar generation. Set `VITE_API_URL` in the frontend to connect.
- **Data (`data/`)** — JSON Schema, reference output, and test fixtures shared by the app and tooling.
- **Avatar generator (`tools/avatar_gen/`)** — LangGraph pipeline that generates `representation_profile`, avatar image, and description from a user's `character_profile`.

## Project structure

```
├── app/                    # React frontend (Vite + TypeScript)
│   └── src/
│       ├── data/           # Types, validation, bundled profiles
│       ├── theme/          # SDUI: deriveTheme, applyTheme, ProfileContext
│       ├── pages/          # Home, Profile, Matches, MatchDetail, EditProfile
│       └── components/     # ProfileSwitcher, layout, etc.
├── api/                    # FastAPI backend (optional live data + avatar jobs)
├── data/
│   ├── schema/             # user-response.schema.json
│   ├── reference/          # sample.json (API output reference)
│   └── test/               # luna, marcus, aria test fixtures
└── tools/
    └── avatar_gen/         # generate.py + requirements
```

## Quick start — frontend

Try the live app at [https://server-driven-ui-fawn.vercel.app/](https://server-driven-ui-fawn.vercel.app/) — use the profile switcher to try bundled users or upload a schema-valid `.json` file.

Run locally:

```bash
cd app
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`).

Build for production:

```bash
npm run build
npm run preview
```

### Deploy to Vercel

Connect this repo in Vercel, set **Root Directory** to `app`, and use the **Vite** preset. Build command: `npm run build`; output directory: `dist`.

Set `VITE_API_URL` in Vercel environment variables when you deploy the FastAPI backend separately.

## Quick start — API (live data)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r api/requirements.txt
copy api\.env.example api\.env

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Connect the frontend:

```bash
cd app
copy .env.example .env   # VITE_API_URL=http://localhost:8000
npm run dev
```

See [`api/README.md`](api/README.md) for endpoints and avatar generation via API.

## Quick start — avatar generator (CLI)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r tools/avatar_gen/requirements.txt
copy tools\avatar_gen\.env.example tools\avatar_gen\.env
# Edit .env with GOOGLE_API_KEY, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN
```

Generate an avatar (overwrites the input and syncs to the web app by default):

```bash
python tools/avatar_gen/generate.py data/test/luna.test.json
```

See [`tools/avatar_gen/README.md`](tools/avatar_gen/README.md) for flags, models, and troubleshooting.

## SDUI theme mapping

Themes are derived deterministically from profile JSON — not from image pixels.

| UI aspect | JSON source |
|-----------|-------------|
| Accent / background colors | `representation_profile.visual_identity.color_palette`, `signature_markings`, `eye_design` |
| Typography | `character_profile.zodiac.element` → font pairing |
| Motion effects | `visual_identity.animation_effects` (with element fallback) |
| Avatar backdrop | `avatar_picture` when `avatar_status === "completed"` |

Key files: `app/src/theme/deriveTheme.ts`, `applyTheme.ts`, `themeMap.ts`.

The API can now generate UI design JSON separately from the base user profile:

```bash
curl -X POST http://localhost:8000/users/4/ui/generate \
  -H "Content-Type: application/json" \
  -d '{"character_profile":{"zodiac":{"sign":"Rat","element":"Water","personality_traits":["calm","patient"]},"horoscope":{"sign":"Cancer","personality_traits":["nurturing","intuitive"]}}}'
curl http://localhost:8000/users/4
```

The second call returns the normal user envelope with the generated UI design merged in, so the frontend can refresh and render the new palette through the existing path.

## Data schema

All profiles validate against `data/schema/user-response.schema.json`. The frontend bundles a copy at `app/src/data/user-response.schema.json` for upload validation via Ajv.

Reference shape: `data/reference/sample.json`.

## Tech stack

| Layer | Tools |
|-------|-------|
| Frontend | React 19, Vite 8, React Router, TypeScript |
| API | FastAPI, Uvicorn, Pydantic |
| Theming | CSS custom properties, chroma-js, @fontsource variable fonts |
| Validation | Ajv + ajv-formats |
| Avatar pipeline | Python, LangGraph, LangChain, Gemini, Cloudflare Workers AI (FLUX) |

## License

Private prototype — add a license if you open-source this repo.
