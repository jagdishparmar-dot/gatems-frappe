#!/bin/bash
set -eo pipefail

BENCH_DIR="/home/frappe/frappe-bench"
cd "${BENCH_DIR}"

SITE="${SITE_NAME:-gatems.localhost}"
ADMIN="${ADMIN_PASSWORD:-${SERVICE_PASSWORD_ADMIN:-admin}}"
MYSQL_ROOT="${MYSQL_ROOT_PASSWORD:-${SERVICE_PASSWORD_MYSQLROOT:-change-me}}"

wait_for_tcp() {
	local host="$1"
	local port="$2"
	echo "Waiting for ${host}:${port}..."
	for _ in $(seq 1 90); do
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

wait_for_tcp "${DB_HOST:-mariadb}" "${DB_PORT:-3306}"

if [ ! -f sites/common_site_config.json ]; then
	echo "Missing sites/common_site_config.json — run configurator first"
	exit 1
fi

if [ ! -d "sites/${SITE}" ]; then
	echo "Creating Frappe site ${SITE}..."
	bench new-site "${SITE}" \
		--force \
		--mariadb-root-password "${MYSQL_ROOT}" \
		--admin-password "${ADMIN}" \
		--no-mariadb-socket
	bench --site "${SITE}" install-app gatems
else
	echo "Site ${SITE} already exists"
	bench --site "${SITE}" install-app gatems || true
	bench --site "${SITE}" migrate || true
fi

PUBLIC_URL="${SERVICE_URL_FRONTEND:-}"
if [ -z "${PUBLIC_URL}" ] && [ -n "${SERVICE_FQDN_FRONTEND:-}" ]; then
	PUBLIC_URL="https://${SERVICE_FQDN_FRONTEND}"
fi
if [ -n "${PUBLIC_URL}" ]; then
	bench --site "${SITE}" set-config host_name "${PUBLIC_URL}"
fi

bench --site "${SITE}" set-config developer_mode "${DEVELOPER_MODE:-0}"
bench --site "${SITE}" set-config socketio_port "${SOCKETIO_PORT:-9000}"
bench --site "${SITE}" enable-scheduler
bench --site "${SITE}" clear-cache
bench use "${SITE}"

echo "GateMS site ready: ${SITE}"
