# Server Driven UI

A TypeScript social app prototype where each user profile drives the entire UI — colors, typography, motion, and avatar backdrop — from a single JSON document. Includes a Python avatar generator that fills in mascot images and visual identity using Gemini and Cloudflare Workers AI.

## What it does

- **Frontend (`app/`)** — React + Vite app themed per user via SDUI. Load bundled profiles or upload any schema-valid JSON; the app derives CSS variables from profile data and reskins instantly.
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
├── data/
│   ├── schema/             # user-response.schema.json
│   ├── reference/          # sample.json (API output reference)
│   └── test/               # luna, marcus, aria test fixtures
└── tools/
    └── avatar_gen/         # generate.py + requirements
```

## Quick start — frontend

```bash
cd app
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). Use the profile switcher to try bundled users or upload a `.json` file.

Build for production:

```bash
npm run build
npm run preview
```

## Quick start — avatar generator

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

## Data schema

All profiles validate against `data/schema/user-response.schema.json`. The frontend bundles a copy at `app/src/data/user-response.schema.json` for upload validation via Ajv.

Reference shape: `data/reference/sample.json`.

## Tech stack

| Layer | Tools |
|-------|-------|
| Frontend | React 19, Vite 8, React Router, TypeScript |
| Theming | CSS custom properties, chroma-js, @fontsource variable fonts |
| Validation | Ajv + ajv-formats |
| Avatar pipeline | Python, LangGraph, LangChain, Gemini, Cloudflare Workers AI (FLUX) |

## License

Private prototype — add a license if you open-source this repo.
