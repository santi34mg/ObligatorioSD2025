#!/bin/bash

# Script to manage development and production environments
# Usage: ./deploy.sh [dev|prod] [up|down|logs|restart]

set -e

MODE=${1:-dev}
ACTION=${2:-up}

COMPOSE_FILE="docker-compose.yml"
if [ "$MODE" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo "Running in $MODE mode using $COMPOSE_FILE"

case $ACTION in
    up)
        echo "Building and starting services..."
        docker-compose -f $COMPOSE_FILE up --build -d
        echo "Services started!"
        echo ""
        echo "Access the application:"
        if [ "$MODE" = "dev" ]; then
            echo "  Frontend (Vite): http://localhost:5173"
        fi
        echo "  Frontend (Traefik): http://localhost"
        echo "  Traefik Dashboard: http://localhost:8081"
        echo "  Grafana: http://localhost:3000"
        echo "  Prometheus: http://localhost:9090"
        ;;
    down)
        echo "Stopping services..."
        docker-compose -f $COMPOSE_FILE down
        echo "Services stopped!"
        ;;
    logs)
        SERVICE=${3:-}
        if [ -z "$SERVICE" ]; then
            docker-compose -f $COMPOSE_FILE logs -f
        else
            docker-compose -f $COMPOSE_FILE logs -f $SERVICE
        fi
        ;;
    restart)
        echo "Restarting services..."
        docker-compose -f $COMPOSE_FILE restart
        echo "Services restarted!"
        ;;
    rebuild)
        SERVICE=${3:-}
        if [ -z "$SERVICE" ]; then
            echo "Rebuilding all services..."
            docker-compose -f $COMPOSE_FILE up --build -d
        else
            echo "Rebuilding $SERVICE..."
            docker-compose -f $COMPOSE_FILE up -d --no-deps --build $SERVICE
        fi
        echo "Rebuild complete!"
        ;;
    ps)
        docker-compose -f $COMPOSE_FILE ps
        ;;
    *)
        echo "Usage: $0 [dev|prod] [up|down|logs|restart|rebuild|ps] [service]"
        echo ""
        echo "Examples:"
        echo "  $0 dev up          # Start development environment"
        echo "  $0 prod up         # Start production environment"
        echo "  $0 dev logs        # View all logs in dev mode"
        echo "  $0 prod logs frontend  # View frontend logs in prod mode"
        echo "  $0 prod rebuild frontend  # Rebuild just the frontend in prod"
        echo "  $0 dev down        # Stop development environment"
        exit 1
        ;;
esac
