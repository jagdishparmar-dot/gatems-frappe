### GateMS

Frappe **Gate Management System** — vehicles, yard board, docks, and fleet tracker. This stack runs **Frappe + GateMS only** (no ERPNext, no HRMS).

### Deploy on Coolify (recommended)

1. In Coolify: **New Resource → Docker Compose**
2. Connect repo: `https://github.com/jagdishparmar-dot/gatems-frappe`
3. Branch: `main`
4. Compose file: `docker-compose.yml`
5. Set environment variables (Coolify can auto-generate passwords):

| Variable | Example | Notes |
|----------|---------|-------|
| `SITE_NAME` | `gatems.yourdomain.com` | Must match your public domain |
| `ADMIN_PASSWORD` | `strong-password` | Frappe Administrator password |
| `MYSQL_ROOT_PASSWORD` | *(generated)* | Or use `SERVICE_PASSWORD_MYSQLROOT` |
| `FRAPPE_SITE_NAME_HEADER` | `$host` | Default; routes by browser Host header |
| `DEVELOPER_MODE` | `0` | Use `1` only for debugging |

6. Assign domain to the **`frontend`** service on port **8080**
   - Coolify reads `SERVICE_FQDN_FRONTEND_8080` from compose and wires Traefik + SSL
7. Deploy and watch logs for `create-site` → `frontend`

First deploy builds the image (`bench init` inside Dockerfile) and can take **10–20 minutes**.

**Login**
- User: **Administrator**
- Password: value of `ADMIN_PASSWORD`
- Demo user (seeded): **gateuser@gatems.local** / **Gatems@123**

**Stack services**
- `frontend` — nginx (public, port 8080)
- `backend` — Frappe web
- `websocket` — realtime / socket.io
- `worker` + `scheduler` — background jobs
- `mariadb` + `redis` — data stores

Data persists in Docker volumes: `mariadb-data`, `sites`, `logs`.

### Local Docker (without Coolify)

```bash
git clone https://github.com/jagdishparmar-dot/gatems-frappe.git
cd gatems-frappe
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
docker compose logs -f create-site frontend
```

Open http://localhost:8080 — site name defaults to `gatems.localhost`.

Stop:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml down
```

Wipe all data:

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml down -v
```

Copy `.env.example` to `.env` to override defaults locally.

### Install on an existing bench

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/jagdishparmar-dot/gatems-frappe.git
bench --site your.site install-app gatems
```

Only the `gatems/` app folder is installed — not the Docker stack.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/gatems
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
