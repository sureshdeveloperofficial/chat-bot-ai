#!/bin/bash

# Build script for Microservice Chatbot
set -e

echo "🚀 Building Microservice Chatbot Project..."

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your OpenAI API key and other settings"
fi

# Build all Docker images
echo "🔨 Building Docker images..."

services=("auth-service" "gateway" "chat-service" "user-service" "vector-service" "frontend")

for service in "${services[@]}"; do
    echo "Building $service..."
    docker build -t chatbot/$service:latest ./$service
done

echo "✅ All images built successfully!"

# Start services
echo "🚢 Starting services with Docker Compose..."
docker-compose up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Health check
echo "🏥 Checking service health..."
services_urls=(
    "http://localhost:8001/health"
    "http://localhost:8002/health" 
    "http://localhost:8003/health"
    "http://localhost:8004/health"
    "http://localhost:8000/health"
)

for url in "${services_urls[@]}"; do
    if curl -f -s "$url" > /dev/null; then
        echo "✅ $(echo $url | cut -d'/' -f3) is healthy"
    else
        echo "❌ $(echo $url | cut -d'/' -f3) is not responding"
    fi
done

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:8501"
echo "   API Gateway: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "👤 Default users:"
echo "   Username: admin, Password: admin123"
echo "   Username: user, Password: user123"
echo ""
echo "📋 To stop services: docker-compose down"
echo "📊 To view logs: docker-compose logs"