#!/bin/bash

# Wait for database
echo "Waiting for database..."
while ! nc -z $DB_HOST 3306; do
  sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations users books
python manage.py migrate


# Seed data (Idempotent script)
echo "Seeding data..."
python seed_data.py

# Start server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
