# Picsal API

Backend API for the Picsal website, structured similarly to the local `product-app-api` reference project while staying intentionally small for now.

## Current Scope

- `core/` for shared models, auth, health, and storage utilities
- `user/` for Supabase-authenticated profile endpoints
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

```bash
python app/manage.py runserver
```

### Docker Development

Start the development stack with:

```bash
docker compose up --build
```

### Future Implementation Notes
5/6/2026 - Break to implement other personal projects.
- Create edit profile endpoint
- Develop a table schema for portfolios and assign images to portfolios
- Create tests for endpoints
- Upgrade api service to eliminate cold start
- Maybe migrate to FastAPI or Node.js?

