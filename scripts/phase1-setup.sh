#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  Salesforce Reports System - Phase 1: Infrastructure Setup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "   Please install Docker from https://www.docker.com/"
    exit 1
fi
echo -e "${GREEN}✓ Docker${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "   Please install Docker Compose from https://docs.docker.com/compose/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${YELLOW}⚠ kubectl is not installed (optional for local dev)${NC}"
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm${NC}"

echo ""
echo -e "${BLUE}🔧 Setting up environment...${NC}"

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Update .env with your Salesforce credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"

# Check if venv exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Created virtual environment${NC}"
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip > /dev/null

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
fi

echo ""
echo -e "${BLUE}📦 Installing Node dependencies...${NC}"

# Check and install frontend dependencies
for frontend in dashboard-fe builder-fe analytics-fe; do
    if [ -f "frontends/$frontend/package.json" ]; then
        echo "   Installing $frontend dependencies..."
        (cd frontends/$frontend && npm install --silent 2>/dev/null)
        echo -e "   ${GREEN}✓ $frontend${NC}"
    fi
done

echo ""
echo -e "${BLUE}🐳 Starting Docker services...${NC}"

# Start Docker services
docker-compose up -d

# Wait for services to be healthy
echo "   Waiting for services to start..."
sleep 5

# Check service health
SERVICES=("redis" "postgres" "elasticsearch" "kibana")
for service in "${SERVICES[@]}"; do
    echo -n "   Checking $service..."
    # Docker compose health check
    if docker-compose exec -T $service true > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${YELLOW}⚠ Starting${NC}"
    fi
done

echo ""
echo -e "${BLUE}✅ Phase 1 Setup Complete${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Next Steps"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Update .env with your Salesforce credentials:"
echo "   SF_CLIENT_ID=your_client_id"
echo "   SF_CLIENT_SECRET=your_client_secret"
echo "   SF_REFRESH_TOKEN=your_refresh_token"
echo ""
echo "2. Access services:"
echo "   - API Gateway: http://localhost (when Phase 2 is complete)"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - Elasticsearch: http://localhost:9200"
echo "   - Kibana: http://localhost:5601"
echo ""
echo "3. Verify services with:"
echo "   make docker-logs        # View Docker logs"
echo "   docker-compose ps       # List running containers"
echo ""
echo "4. For Kubernetes deployment:"
echo "   make k8s-setup          # Setup Kubernetes infrastructure"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
