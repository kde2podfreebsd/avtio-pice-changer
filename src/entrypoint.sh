#!/bin/bash
echo "Running migrations"
export PYTHONPATH="${PYTHONPATH}"
alembic revision --autogenerate
alembic upgrade head 
/usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf