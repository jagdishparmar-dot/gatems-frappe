#!/bin/bash
set -eo pipefail

BENCH_DIR="/home/frappe/frappe-bench"
cd "${BENCH_DIR}"

mkdir -p sites logs
ls -1 apps > sites/apps.txt

bench set-config -g db_host "${DB_HOST:-mariadb}"
bench set-config -gp db_port "${DB_PORT:-3306}"
bench set-config -g redis_cache "redis://${REDIS_HOST:-redis}:${REDIS_PORT:-6379}"
bench set-config -g redis_queue "redis://${REDIS_HOST:-redis}:${REDIS_PORT:-6379}"
bench set-config -g redis_socketio "redis://${REDIS_HOST:-redis}:${REDIS_PORT:-6379}"
bench set-config -gp socketio_port "${SOCKETIO_PORT:-9000}"

echo "GateMS bench configured:"
cat sites/common_site_config.json
