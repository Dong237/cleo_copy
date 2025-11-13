#!/bin/bash

# Setup script for local development

echo "🚀 Setting up Cleo Financial Assistant development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ml/models
mkdir -p logs
mkdir -p tmp

# Create .gitkeep files
touch ml/models/.gitkeep

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d postgres redis rabbitmq

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
./scripts/run-migrations.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Start all services: docker-compose up"
echo "  3. Access services:"
echo "     - User Service: http://localhost:8001"
echo "     - Banking Service: http://localhost:8002"
echo "     - Budget Service: http://localhost:8003"
echo "     - Chat Service: http://localhost:8004"
echo "     - API Gateway (Kong): http://localhost:8000"
echo "     - PostgreSQL: localhost:5432"
echo "     - Redis: localhost:6379"
echo "     - RabbitMQ Management: http://localhost:15672"
echo "     - pgAdmin: http://localhost:5050"
echo ""
echo "📖 Documentation: docs/README.md"
