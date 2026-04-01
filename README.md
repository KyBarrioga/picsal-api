# Picsal API

Backend API for the Picsal website, structured similarly to the local `product-app-api` reference project while staying intentionally small for now.

## Current Scope

- `core/` for shared models, auth, health, and storage utilities
- `user/` for Supabase-authenticated profile endpoints
- Supabase Auth + your existing `profiles` table as the source of truth
- Supabase Auth JWT verification for request authentication
- Cloudflare R2 signed upload support for image storage

## Project Structure

- `app/app/` Django project configuration
- `app/core/` shared auth classes and infrastructure endpoints
- `app/user/` user profile API

## Setup

1. Create and activate a virtual environment.
2. Use Python 3.14.x and install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements.development.txt
```

3. Copy `.env.example` to `.env` and fill in your Supabase and Cloudflare R2 credentials.
4. Point `DATABASE_URL` at your existing Supabase Postgres database.
   For Docker and other persistent backends without reliable IPv6, prefer the Supabase session pooler string with `sslmode=require`.
5. If you need to override where Django writes collected static files, set `DJANGO_STATIC_ROOT`.
6. Start the API:

```bash
python app/manage.py runserver
```

### Docker Development

This project follows the same overall Docker approach as `product-app-api`:

- app container for Django
- production image entrypoint via `scripts/run.sh`

Start the development stack with:

```bash
docker compose up --build
```

Notes:

- Docker now expects `DATABASE_URL` to point at your real Supabase database
- this repo no longer owns the database schema or migrations
- production containers default `DJANGO_STATIC_ROOT` to `/vol/web/static`, which matches the writable volume created in the Docker image

## API Endpoints

- `GET /api/health/` health check
- `POST /api/auth/login/` password login via Supabase Auth
- `GET /api/user/me/` authenticated user info plus the matching Supabase `profiles` row
- `PATCH /api/user/me/` update editable fields on the authenticated user's Supabase `profiles` row
- `POST /api/core/storage/presign/` generate a signed Cloudflare R2 upload URL
- `GET /api/docs/swagger/` Swagger UI
- `GET /api/docs/redoc/` ReDoc

## Auth Model

The API expects a Supabase access token in the `Authorization: Bearer <token>` header. On each authenticated request, the backend:

- validates the JWT with your `SUPABASE_JWT_SECRET`
- validates the JWT with `SUPABASE_JWKS_URL` for modern Supabase signing keys, or falls back to `SUPABASE_JWT_SECRET` for legacy projects
- reads the user id from the `sub` claim
- uses that identity to read and update your existing Supabase `profiles` row
- relies on Supabase to own auth, profile records, and database rules
