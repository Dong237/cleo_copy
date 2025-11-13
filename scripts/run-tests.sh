#!/bin/bash

# Run all tests with coverage

echo "🧪 Running Cleo Test Suite..."

# Activate virtual environment if needed
# source venv/bin/activate

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r backend/tests/requirements.txt

# Run tests with coverage
echo "🏃 Running tests..."
pytest backend/tests/ \
    -v \
    --cov=backend/services \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo "❌ Some tests failed!"
    exit 1
fi
