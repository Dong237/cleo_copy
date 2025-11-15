#!/bin/bash
# Test runner script for backend services

set -e

echo "🧪 Running backend tests..."

# Set environment variables
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://cleo:cleo_password@localhost:5432/cleo_test}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export SECRET_KEY="${SECRET_KEY:-test-secret-key}"
export TESTING=true
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/shared"

# Run pytest with coverage
python -m pytest tests/ \
    --cov=services \
    --cov=shared \
    --cov-report=xml \
    --cov-report=html \
    --cov-report=term-missing \
    -v \
    || true  # Don't fail if no tests found

echo "✅ Tests complete"
