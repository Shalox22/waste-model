#!/bin/bash

# Trash Detection API - Docker Deployment Script
# Usage: ./deploy.sh [start|stop|restart|logs|build]

set -e

PROJECT_NAME="trash-detector"
IMAGE_NAME="trash-detector:latest"

echo "================================"
echo "Trash Detection API - Docker"
echo "================================"

case "${1:-start}" in
    start)
        echo "Starting Docker containers..."
        docker-compose up -d
        echo "✓ API started! Access it at http://localhost:8080"
        echo "✓ API documentation: http://localhost:8080/docs"
        ;;
    
    stop)
        echo "Stopping Docker containers..."
        docker-compose down
        echo "✓ Containers stopped"
        ;;
    
    restart)
        echo "Restarting Docker containers..."
        docker-compose down
        docker-compose up -d
        echo "✓ Containers restarted"
        ;;
    
    logs)
        echo "Showing container logs (Ctrl+C to exit)..."
        docker-compose logs -f trash-detector
        ;;
    
    build)
        echo "Building Docker image..."
        docker build -t $IMAGE_NAME .
        echo "✓ Image built successfully"
        ;;
    
    clean)
        echo "Cleaning up Docker resources..."
        docker-compose down -v
        docker rmi $IMAGE_NAME
        echo "✓ Cleanup complete"
        ;;
    
    status)
        echo "Checking container status..."
        docker-compose ps
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|logs|build|clean|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the API server"
        echo "  stop    - Stop the API server"
        echo "  restart - Restart the API server"
        echo "  logs    - View container logs"
        echo "  build   - Build the Docker image"
        echo "  clean   - Remove all containers and images"
        echo "  status  - Show container status"
        exit 1
        ;;
esac
