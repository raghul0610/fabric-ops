# FABRIC Ops Frontend

## Local setup

1. Copy `.env.example` to `.env`.
2. Set `VITE_SUPABASE_PUBLISHABLE_KEY` from the FABRIC Supabase project.
3. Keep `VITE_API_BASE_URL=http://localhost:8000` for the local FastAPI server.
4. From `frontend/`, run:

```bash
npm install
npm run typecheck
npm run build
npm run dev
```

The browser only receives the Supabase publishable key. Never put the Supabase service-role key in `.env`, source code, or a Vite build.

The backend must have `FRONTEND_ORIGIN=http://localhost:5173` in its environment for local API requests.
