#!/usr/bin/env bash

# Postgres full database backup script (production-friendly)
# - Supports PG connection URI via PG_URI or discrete env vars (PGHOST, PGPORT, PGUSER, PGDATABASE)
# - Stores backups locally with rotation
# - No secrets are stored in this file; use ~/.pgpass or environment variables

set -euo pipefail

LOG_PREFIX="[pg_backup]"

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/c0r-ai/postgres}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
FILENAME="postgres_${TIMESTAMP}.dump"
BACKUP_PATH="${BACKUP_DIR}/${FILENAME}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

# Ensure SSL to Supabase by default
export PGSSLMODE="${PGSSLMODE:-require}"

echo "${LOG_PREFIX} Starting backup at $(date -Is)"

# Ensure pg_dump is available
if ! command -v pg_dump >/dev/null 2>&1; then
  echo "${LOG_PREFIX} ERROR: pg_dump not found. Install postgresql-client." >&2
  exit 1
fi

# Prepare backup directory
mkdir -p "${BACKUP_DIR}"
chmod 700 "${BACKUP_DIR}" || true

resolve_ipv4() {
  local host="$1"
  local ip=""
  if command -v getent >/dev/null 2>&1; then
    ip=$(getent ahostsv4 "$host" | awk 'NR==1{print $1}') || true
    if [[ -z "$ip" ]]; then
      ip=$(getent hosts "$host" | awk '/^[0-9.]+/{print $1; exit}') || true
    fi
  fi
  if [[ -z "$ip" && $(command -v dig >/dev/null 2>&1; echo $?) -eq 0 ]]; then
    ip=$(dig +short A "$host" | head -1) || true
  fi
  echo -n "$ip"
}

# Prefer IPv4 if the host has AAAA but IPv6 is not reachable
if [[ -n "${PGHOST:-}" && -z "${PGHOSTADDR:-}" ]]; then
  IPV4_ADDR=$(resolve_ipv4 "$PGHOST")
  if [[ -n "${IPV4_ADDR:-}" ]]; then
    export PGHOSTADDR="$IPV4_ADDR"
    echo "${LOG_PREFIX} Using IPv4 PGHOSTADDR=${PGHOSTADDR} for host ${PGHOST}"
  fi
fi

# Build pg_dump command
PG_DUMP_CMD=(pg_dump -F c -f "${BACKUP_PATH}")

if [[ -n "${PG_URI:-}" ]]; then
  # Use connection string
  PG_DUMP_CMD+=("${PG_URI}")
else
  # Use discrete connection params; rely on ~/.pgpass for password
  : "${PGHOST:?PGHOST is required if PG_URI is not set}"
  : "${PGPORT:?PGPORT is required if PG_URI is not set}"
  : "${PGUSER:?PGUSER is required if PG_URI is not set}"
  : "${PGDATABASE:?PGDATABASE is required if PG_URI is not set}"
  PG_DUMP_CMD+=(-h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}")
fi

echo "${LOG_PREFIX} Writing backup to ${BACKUP_PATH}"

# Run backup
if ! "${PG_DUMP_CMD[@]}"; then
  echo "${LOG_PREFIX} ERROR: pg_dump failed" >&2
  exit 1
fi

# Quick integrity check (list archive contents)
if ! pg_restore -l "${BACKUP_PATH}" >/dev/null 2>&1; then
  echo "${LOG_PREFIX} ERROR: backup integrity check failed for ${BACKUP_PATH}" >&2
  exit 1
fi

echo "${LOG_PREFIX} Backup completed: ${BACKUP_PATH}"

# Retention policy: remove files older than RETENTION_DAYS
echo "${LOG_PREFIX} Applying retention: ${RETENTION_DAYS} days"
find "${BACKUP_DIR}" -type f -name "postgres_*.dump" -mtime +"${RETENTION_DAYS}" -print -delete || true

echo "${LOG_PREFIX} Done at $(date -Is)"


