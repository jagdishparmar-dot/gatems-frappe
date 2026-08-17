### GateMS

Frappe **Gate Management System** — vehicles, yard board, docks, and fleet tracker. This stack runs **Frappe + GateMS only** (no ERPNext, no HRMS).

### Deploy with Docker

```bash
git clone https://github.com/jagdishparmar-dot/gatems-frappe.git
cd gatems-frappe
docker compose up -d
```

First start clones Frappe and can take several minutes. Follow logs with:

```bash
docker compose logs -f frappe
```

- App: http://localhost:8080
- Login: **Administrator** / **admin**
- GateMS user: **gateuser@gatems.local** / **Gatems@123**

Ports: **8080** (web) and **9001** (realtime / socketio).

Stop:

```bash
docker compose down
```

Data stays in the `gatems-mariadb-data` Docker volume. To wipe and start clean:

```bash
docker compose down -v
```

### Install on an existing bench

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/jagdishparmar-dot/gatems-frappe.git
bench --site your.site install-app gatems
```

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
