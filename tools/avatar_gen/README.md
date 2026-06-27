# Avatar Generator

Fills in the missing avatar fields of a user JSON (the `representation_profile`,
`avatar_picture`, `avatar_description`, `avatar_status`,
`avatar_generation_started_at`) from the user's `character_profile`.

Pipeline (LangGraph):

```
persona (Gemini) -> image prompt -> image (Cloudflare FLUX/SDXL) -> host
   -> description (Gemini) -> assemble -> validate vs schema -> (retry | done)
```

- **Text / persona:** Google Gemini via `langchain-google-genai`, using structured
  output so the generated `representation_profile` matches the schema shape.
- **Images:** Cloudflare Workers AI (FLUX-1-schnell by default, or SDXL).
- **Hosting:** the generated image is uploaded to catbox.moe (free, keyless) so
  `avatar_picture` is a real public `https` URL.
- **Validation:** the assembled object is checked against
  `data/schema/user-response.schema.json`; on failure the graph retries.

Profiles copied into `app/src/data/profiles/` appear in the live web app at
[https://server-driven-ui-fawn.vercel.app/](https://server-driven-ui-fawn.vercel.app/)
after you redeploy (or locally via `npm run dev` in `app/`).

## Setup

```bash
# from the repo root
python -m venv .venv
.venv\Scripts\activate            # Windows PowerShell
pip install -r tools/avatar_gen/requirements.txt

copy tools\avatar_gen\.env.example tools\avatar_gen\.env   # then edit .env
```

Required environment variables (see `.env.example`):

- `GOOGLE_API_KEY` - Gemini key from https://aistudio.google.com/apikey
- `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` - a Workers AI token
- optional: `GEMINI_MODEL`, `CF_IMAGE_MODEL`, `HOST_IMAGES`, `MAX_ATTEMPTS`, `OUT_DIR`

## Usage

The whole pipeline is a single script: `generate.py`.

```bash
# default: overwrites the input in place AND copies it into the web app
python tools/avatar_gen/generate.py data/test/luna.test.json

# write to a separate file instead of overwriting the input
python tools/avatar_gen/generate.py data/test/luna.test.json --no-in-place
python tools/avatar_gen/generate.py data/test/luna.test.json --out data/out/luna.json

# don't copy into the web app
python tools/avatar_gen/generate.py data/test/luna.test.json --no-apply-to-app

# skip hosting and use a local file:// URI instead
python tools/avatar_gen/generate.py data/test/luna.test.json --no-host
```

By default the profile is written to `app/src/data/profiles/<name>.json`. The app
auto-discovers everything in that folder (via `import.meta.glob`), so it appears in
the switcher with no further edits. Pass `--no-apply-to-app` to skip this.

The input may be either the full API envelope (`{ "code", "message", "data" }`)
or just the `data` object; the output preserves whichever shape was given.

## Notes

- Using SDXL instead of FLUX: set `CF_IMAGE_MODEL=@cf/stabilityai/stable-diffusion-xl-base-1.0`.
  FLUX returns a base64 image (JSON); SDXL returns binary PNG. Both are handled.
- `avatar_picture` is a `uri` in the schema, so a hosted `https` URL (default) or a
  `file://` URI (`--no-host`) is used - never a bare relative path.
- Generated profiles appear in the web app's switcher automatically (they're copied
  into `app/src/data/profiles/`, which the app auto-loads). Use `--no-apply-to-app`
  to opt out. To see new profiles on the live demo, commit the updated JSON and let
  Vercel redeploy.
