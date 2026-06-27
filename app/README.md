# Astrana frontend

React + Vite + TypeScript app for the server-driven UI prototype. Each user profile JSON drives colors, typography, motion, and avatar backdrop via CSS custom properties.

**Live demo:** [https://server-driven-ui-fawn.vercel.app/](https://server-driven-ui-fawn.vercel.app/)

## Development

```bash
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). Use the profile switcher to try bundled users or upload a schema-valid `.json` file.

## Build

```bash
npm run build
npm run preview
```

Production output goes to `dist/`.

## Deploy (Vercel)

This app is deployed at [https://server-driven-ui-fawn.vercel.app/](https://server-driven-ui-fawn.vercel.app/).

| Setting | Value |
| --- | --- |
| Root Directory | `app` |
| Framework Preset | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |

The app uses `BrowserRouter` for client-side routes (`/matches`, `/profile`, etc.). If deep links return 404 after deploy, add a `vercel.json` rewrite to `index.html`.

## Project layout

```
src/
├── data/       # Types, validation, bundled profiles
├── theme/      # SDUI: deriveTheme, applyTheme, ProfileContext
├── pages/      # Home, Profile, Matches, MatchDetail, EditProfile
└── components/ # ProfileSwitcher, layout, UI primitives
```

See the repo root [README](../README.md) for SDUI theme mapping, data schema, and avatar generator tooling.

## Lint

```bash
npm run lint
```

Uses [Oxlint](https://oxc.rs/docs/guide/usage/linter.html) with React rules in `.oxlintrc.json`.
