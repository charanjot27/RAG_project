# VeriFin — React frontend

A professional single-page UI for the VeriFin API: live demo (all 3 retrieval
modes), faithfulness gauge, green/red cited sentences, abstention banner, stage
timings, plus How-it-works, benchmark, and About sections for promotion.

## Run it (dev)

The backend must be running first:

```bash
# from the repo root — start the API on :8000
uvicorn api.main:app --port 8000
```

Then, in this folder:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. In dev, calls to `/api/*` are proxied to the backend
on `:8000` (see `vite.config.ts`), so there are no CORS issues.

## Build for production

```bash
npm run build      # outputs static files to dist/
npm run preview    # preview the production build locally
```

Point the built app at your deployed API by setting `VITE_API_URL` at build time:

```bash
VITE_API_URL="https://your-verifin-api.onrender.com" npm run build
```

Deploy the `dist/` folder to any static host (Vercel, Netlify, GitHub Pages,
Cloudflare Pages). The backend's CORS is open by default (`ALLOWED_ORIGINS=*`);
lock it to your frontend's URL for production.

## What it talks to

- `POST /api/ask` `{ question, mode }` → verified answer (sentences, faithfulness,
  abstention, sources, timings)
- `GET /api/health` → liveness + index readiness

Modes: `local` (your indexed docs), `web` (live web search), `web_cached`
(web + Qdrant cache for instant repeats).
