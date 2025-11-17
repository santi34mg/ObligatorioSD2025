#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== UMShare Monitoring Health Check ===${NC}\n"

# Function to check if a URL is accessible
check_url() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    printf "Checking %-30s ... " "$name"
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_code" ]; then
            echo -e "${GREEN}OK${NC} (HTTP $response)"
            return 0
        else
            echo -e "${YELLOW}Warning${NC} (HTTP $response, expected $expected_code)"
            return 1
        fi
    else
        echo -e "${RED}Failed${NC} (Connection failed)"
        return 1
    fi
}

# Check main monitoring services
echo -e "${YELLOW}Main Monitoring Services:${NC}"
check_url "Prometheus" "http://localhost:9090/-/healthy"
check_url "Grafana" "http://localhost:3000/api/health"

echo -e "\n${YELLOW}Microservices Health Endpoints:${NC}"
check_url "Auth Service" "http://localhost:8002/api/auth/register"
check_url "Friendship Service" "http://localhost:8007/api/friendships/health"
check_url "Users Service" "http://localhost:8008/api/users/health"
check_url "Content Service" "http://localhost:8001/api/content/health"

echo -e "\n${YELLOW}Microservices Metrics Endpoints:${NC}"
check_url "Auth Service Metrics" "http://localhost:8002/metrics"
check_url "Friendship Service Metrics" "http://localhost:8007/metrics"
check_url "Users Service Metrics" "http://localhost:8008/metrics"
check_url "Content Service Metrics" "http://localhost:8001/metrics"
check_url "Collaboration Service Metrics" "http://localhost:8003/metrics"
check_url "WebSocket Service Metrics" "http://localhost:8005/metrics"
check_url "Communication Service Metrics" "http://localhost:8006/metrics"

echo -e "\n${YELLOW}Infrastructure Metrics:${NC}"
check_url "Traefik Metrics" "http://localhost:8082/metrics"
check_url "RabbitMQ Metrics" "http://localhost:15692/metrics"

echo -e "\n${GREEN}=== Prometheus Targets Status ===${NC}"
if command -v jq &> /dev/null; then
    curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | "\(.labels.job): \(.health)"' | while read line; do
        job=$(echo $line | cut -d: -f1)
        health=$(echo $line | cut -d: -f2 | xargs)
        printf "%-30s ... " "$job"
        if [ "$health" == "up" ]; then
            echo -e "${GREEN}UP${NC}"
        else
            echo -e "${RED}DOWN${NC}"
        fi
    done
else
    echo -e "${YELLOW}Install 'jq' for detailed target status${NC}"
    echo "Run: sudo apt-get install jq (Ubuntu/Debian) or brew install jq (macOS)"
fi

echo -e "\n${GREEN}=== Access Information ===${NC}"
echo -e "Prometheus:  ${YELLOW}http://localhost:9090${NC} or ${YELLOW}http://prometheus.localhost${NC}"
echo -e "Grafana:     ${YELLOW}http://localhost:3000${NC} or ${YELLOW}http://grafana.localhost${NC}"
echo -e "             Username: ${YELLOW}admin${NC}, Password: ${YELLOW}admin${NC}"
echo -e "Traefik:     ${YELLOW}http://localhost:8081${NC}"
echo -e "RabbitMQ:    ${YELLOW}http://rabbitmq.localhost${NC}"

echo -e "\n${GREEN}=== Quick Commands ===${NC}"
echo -e "View Prometheus targets:  ${YELLOW}curl http://localhost:9090/api/v1/targets | jq${NC}"
echo -e "View service metrics:     ${YELLOW}curl http://localhost:8002/metrics${NC}"
echo -e "Restart monitoring:       ${YELLOW}docker-compose restart prometheus grafana${NC}"
echo -e "View logs:                ${YELLOW}docker-compose logs -f prometheus grafana${NC}"

echo ""
