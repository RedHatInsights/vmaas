#!/bin/sh

exec /app/wait-for-postgres.sh /app/app.py
