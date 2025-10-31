#!/bin/sh
set -e

echo "=== Nginx Entrypoint ==="
echo "ACTIVE_POOL: ${ACTIVE_POOL}"
echo "PORT: ${PORT:-3000}"

if [ "${ACTIVE_POOL}" = "blue" ]; then
    BACKUP_POOL="green"
elif [ "${ACTIVE_POOL}" = "green" ]; then
    BACKUP_POOL="blue"
else
    echo "ERROR: ACTIVE_POOL must be 'blue' or 'green'"
    exit 1
fi

export ACTIVE_POOL
export BACKUP_POOL
export PORT

envsubst '${ACTIVE_POOL} ${BACKUP_POOL} ${PORT}' \
    < /etc/nginx/nginx.conf.template \
    > /etc/nginx/nginx.conf

nginx -t
exec nginx -g 'daemon off;'