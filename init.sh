#!/bin/bash
set -eo pipefail

if [ -n "${NODE_VERSION_DEVELOP:-}" ] && [ -n "${NVM_DIR:-}" ]; then
	export PATH="${NVM_DIR}/versions/node/v${NODE_VERSION_DEVELOP}/bin/:${PATH}"
fi

SITE="${SITE:-gatems.localhost}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-123}"
APP_SRC="/workspace/gatems"
BENCH_DIR="/home/frappe/frappe-bench"

wait_for_tcp() {
	local host="$1"
	local port="$2"
	echo "Waiting for ${host}:${port}..."
	for _ in $(seq 1 60); do
		if python3 - <<PY
import socket, sys
s = socket.socket()
s.settimeout(2)
try:
    s.connect(("${host}", ${port}))
except Exception:
    sys.exit(1)
finally:
    s.close()
sys.exit(0)
PY
		then
			echo "${host}:${port} is up"
			return 0
		fi
		sleep 2
	done
	echo "Timed out waiting for ${host}:${port}"
	return 1
}

link_gatems() {
	ln -sfn "${APP_SRC}" "${BENCH_DIR}/apps/gatems"
	mkdir -p "${BENCH_DIR}/sites"
	if [ -f "${BENCH_DIR}/sites/apps.txt" ]; then
		[ -z "$(tail -c1 "${BENCH_DIR}/sites/apps.txt")" ] || echo >> "${BENCH_DIR}/sites/apps.txt"
		grep -qx 'gatems' "${BENCH_DIR}/sites/apps.txt" || echo gatems >> "${BENCH_DIR}/sites/apps.txt"
	fi
	"${BENCH_DIR}/env/bin/python" -m pip install -e "${BENCH_DIR}/apps/gatems" --quiet || true
}

patch_procfile() {
	local procfile="${BENCH_DIR}/Procfile"
	if [ -f "${procfile}" ]; then
		sed -i '/redis/d' "${procfile}"
		sed -i '/watch/d' "${procfile}"
		sed -i 's/bench serve.*/bench serve --host 0.0.0.0 --port 8000/' "${procfile}"
	fi
}

fix_apps_txt() {
	local apps_txt="${BENCH_DIR}/sites/apps.txt"
	[ -f "${apps_txt}" ] || return 0
	python3 - <<'PY'
from pathlib import Path

path = Path("/home/frappe/frappe-bench/sites/apps.txt")
text = path.read_text().replace("frappegatems", "frappe\ngatems")
apps = []
for line in text.splitlines():
	name = line.strip()
	if name and name not in apps:
		apps.append(name)
path.write_text("\n".join(apps) + "\n")
print("apps.txt ->", path.read_text().strip())
PY
}

cd /home/frappe
wait_for_tcp mariadb 3306
wait_for_tcp redis 6379

if [ ! -d "${BENCH_DIR}/apps/frappe" ]; then
	echo "Creating GateMS bench (Frappe + GateMS only)..."
	bench init --skip-redis-config-generation frappe-bench
	cd "${BENCH_DIR}"
	bench set-mariadb-host mariadb
	bench set-redis-cache-host redis://redis:6379
	bench set-redis-queue-host redis://redis:6379
	bench set-redis-socketio-host redis://redis:6379
	patch_procfile
	fix_apps_txt
	bench new-site "${SITE}" \
		--force \
		--mariadb-root-password "${MYSQL_ROOT_PASSWORD}" \
		--admin-password "${ADMIN_PASSWORD}" \
		--no-mariadb-socket
	link_gatems
	bench --site "${SITE}" install-app gatems
	bench --site "${SITE}" set-config developer_mode 1
	bench --site "${SITE}" set-config socketio_port 9001
	bench --site "${SITE}" enable-scheduler
	bench --site "${SITE}" clear-cache
	bench use "${SITE}"
else
	echo "Bench already exists, starting GateMS..."
	cd "${BENCH_DIR}"
	patch_procfile
	fix_apps_txt
	if [ ! -d "sites/${SITE}" ]; then
		bench new-site "${SITE}" \
			--force \
			--mariadb-root-password "${MYSQL_ROOT_PASSWORD}" \
			--admin-password "${ADMIN_PASSWORD}" \
			--no-mariadb-socket
	fi
	link_gatems
	bench --site "${SITE}" install-app gatems || true
	bench --site "${SITE}" set-config developer_mode 1 || true
	bench --site "${SITE}" set-config socketio_port 9001 || true
	bench use "${SITE}" || true
fi

cd "${BENCH_DIR}"
exec bench start
