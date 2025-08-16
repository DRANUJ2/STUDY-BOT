#!/bin/bash

# Study Bot Docker Build Script

set -e

echo "🐳 Building Study Bot Docker Image"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the image
echo "🔨 Building Docker image..."
docker build -t study-bot:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    
    # Test the image
    echo "🧪 Testing Docker image..."
    
    # Run a test container
    echo "🚀 Starting test container..."
    docker run -d --name study-bot-test study-bot:latest
    
    # Wait a moment for the container to start
    sleep 5
    
    # Check container status
    if docker ps | grep -q study-bot-test; then
        echo "✅ Container is running successfully!"
        
        # Show container logs
        echo "📋 Container logs:"
        docker logs study-bot-test --tail 20
        
        # Stop and remove test container
        echo "🛑 Stopping test container..."
        docker stop study-bot-test
        docker rm study-bot-test
        
        echo "🎉 Docker build and test completed successfully!"
        echo ""
        echo "📋 To run the bot:"
        echo "   docker run -d --name study-bot -p 8080:8080 study-bot:latest"
        echo ""
        echo "📋 To view logs:"
        echo "   docker logs -f study-bot"
        echo ""
        echo "📋 To stop the bot:"
        echo "   docker stop study-bot"
        
    else
        echo "❌ Container failed to start"
        docker logs study-bot-test
        docker stop study-bot-test 2>/dev/null || true
        docker rm study-bot-test 2>/dev/null || true
        exit 1
    fi
    
else
    echo "❌ Docker build failed!"
    exit 1
fi
