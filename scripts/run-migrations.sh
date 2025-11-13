#!/bin/bash

# Database migration script

echo "🔄 Running database migrations..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U cleo; do
  sleep 1
done

echo "✅ PostgreSQL is ready"

# Run migrations by executing SQL files in order
echo "📝 Executing schema files..."

for file in database/schemas/*.sql; do
  echo "  - Executing $(basename $file)"
  docker-compose exec -T postgres psql -U cleo -d cleo_db -f /docker-entrypoint-initdb.d/$(basename $file)
done

echo "✅ All migrations completed successfully!"
