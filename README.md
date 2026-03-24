# Picsal API

Backend API for the Picsal website, structured similarly to the local `product-app-api` reference project while staying intentionally small for now.

## Current Scope

- `core/` for shared models, auth, health, and storage utilities
- `user/` for Supabase-authenticated profile endpoints
- Supabase Postgres as the application database
- Supabase Auth JWT verification for request authentication
- Cloudflare R2 signed upload support for image storage
- Supabase SQL migration for row-level security policies

## Project Structure

- `app/app/` Django project configuration
- `app/core/` shared models, auth classes, permissions, and infrastructure endpoints
- `app/user/` user profile API
- `supabase/migrations/` SQL to run in Supabase for schema and RLS

## Setup

1. Create and activate a virtual environment.
2. Use Python 3.14.x and install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements.development.txt
```

3. Copy `.env.example` to `.env` and fill in your Supabase and Cloudflare R2 credentials.
4. Run the Supabase SQL migration from `supabase/migrations/0001_picsal_core.sql`.
5. Apply Django migrations:

```bash
python app/manage.py migrate
```

6. Start the API:

```bash
python app/manage.py runserver
```

### Docker Development

This project follows the same overall Docker approach as `product-app-api`:

- app container for Django
- separate Postgres container for local development
- production image entrypoint via `scripts/run.sh`

Start the development stack with:

```bash
docker compose up --build
```

Notes:

- local Docker uses the `db` service, not Supabase
- deployed environments can point the same app image at Supabase by setting `DATABASE_URL`
- you should still run the SQL in `supabase/migrations/0001_picsal_core.sql` in your real Supabase project for production RLS

## API Endpoints

- `GET /api/health/` health check
- `GET /api/user/me/` current Supabase user profile
- `PATCH /api/user/me/` update the authenticated user's profile fields
- `POST /api/core/storage/presign/` generate a signed Cloudflare R2 upload URL
- `GET /api/docs/swagger/` Swagger UI
- `GET /api/docs/redoc/` ReDoc

## Auth Model

The API expects a Supabase access token in the `Authorization: Bearer <token>` header. On each authenticated request, the backend:

- validates the JWT with your `SUPABASE_JWT_SECRET`
- reads the user id from the `sub` claim
- syncs a `user_profiles` row for that user
- maps the effective role from Supabase `app_metadata.picsal_role`

Supported roles:

- `user`
- `admin`
- `superuser`

## RLS Rules

The Supabase migration creates `public.user_profiles` and enables RLS so that:

- `admin` and `superuser` can create, update, delete, and view all rows
- `user` can view and update only their own row

Those policies depend on `auth.jwt()->'app_metadata'->>'picsal_role'`.
