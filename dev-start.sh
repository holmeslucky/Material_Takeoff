#!/bin/bash

echo "Capitol Engineering - Takeoff Application Development Startup"
echo "=============================================================="
echo

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo
    echo "IMPORTANT: Please edit .env file with your OpenAI API key"
    echo "Your OpenAI key: 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"
    echo
    read -p "Press Enter to continue..."
fi

echo "Starting development environment..."
echo

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker first."
    exit 1
fi

echo "Building and starting services..."
docker-compose up --build -d

echo
echo "Services starting up..."
echo "- Frontend: http://localhost:7000"
echo "- Backend API: http://localhost:8000"
echo "- Full App (Nginx): http://localhost:80"
echo "- Database: localhost:5432"
echo

echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo "Checking service status..."
docker-compose ps

echo
echo "Development environment ready!"
echo
echo "Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Stop services: docker-compose down"
echo "- Rebuild: docker-compose up --build"
echo