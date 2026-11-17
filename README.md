# GradIntel

Upload study documents, then get summaries, quizzes and a RAG chatbot over them.

| Service    | Tech                          | Exposed                        |
|------------|-------------------------------|--------------------------------|
| `frontend` | React + Vite, served by Caddy | ports 80/443, HTTPS automatic  |
| `backend`  | FastAPI + SQLModel            | via `/api` and `/docs` only    |
| `db`       | PostgreSQL 17 + pgvector      | 127.0.0.1:5432 only            |

Everything runs on one domain: the app is at `https://api.nasser-dev.om/`,
the API at `https://api.nasser-dev.om/api/v1/` and its docs at `/docs`.

## Deploy to api.nasser-dev.om

1. **DNS:** create an `A` record `api.nasser-dev.om` → your server's public IP.
2. **Firewall:** open ports 80 and 443 (needed for the Let's Encrypt certificate).
3. **Ollama** (embeddings) on the server: install it, `ollama pull embeddinggemma`,
   and make it listen on all interfaces: `OLLAMA_HOST=0.0.0.0 ollama serve`.
4. On the server:

   ```bash
   git clone <repo> gradintel && cd gradintel
   cp .env.example .env     # then set SECRET_KEY, passwords, GEMINI_API_KEY
   docker compose up -d --build
   ```

The backend runs migrations and creates the first superuser on start.
Logs: `docker compose logs -f backend`.

## Local development

Run only the database in Docker, and the backend and frontend directly:

```bash
docker compose up -d db                      # Postgres on localhost:5432
cd backend && uv sync && fastapi dev app/main.py
cd frontend && npm install && npm run dev    # http://localhost:5173
```

Or run the whole stack locally with `DOMAIN=localhost` in `.env` and open
`https://localhost` (Caddy uses a self-signed local certificate).

## Regenerating the frontend API client

After changing backend routes: `bash scripts/generate-client.sh`.
