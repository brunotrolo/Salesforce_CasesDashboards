.PHONY: help setup install test lint docker-up docker-down clean k8s-setup k8s-deploy k8s-down

help:
	@echo "Salesforce Reports System - Available commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make setup           - Setup local environment (install + docker-up)"
	@echo "  make install         - Install dependencies (Python + Node)"
	@echo ""
	@echo "🐳 Docker (Development):"
	@echo "  make docker-up       - Start Docker services (local dev)"
	@echo "  make docker-down     - Stop Docker services"
	@echo "  make docker-logs     - View Docker logs"
	@echo ""
	@echo "☸️  Kubernetes (Production):"
	@echo "  make k8s-setup       - Setup Kubernetes namespace & infrastructure"
	@echo "  make k8s-deploy      - Deploy all services to Kubernetes"
	@echo "  make k8s-down        - Remove all Kubernetes resources"
	@echo "  make k8s-logs        - View Kubernetes logs"
	@echo ""
	@echo "✅ Testing & Quality:"
	@echo "  make test            - Run tests (Python + Node)"
	@echo "  make test-backend    - Run backend tests only"
	@echo "  make test-frontend   - Run frontend tests only"
	@echo "  make lint            - Run linters (Python + Node)"
	@echo "  make lint-backend    - Lint backend code"
	@echo "  make lint-frontend   - Lint frontend code"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean           - Clean all generated files"
	@echo "  make env-setup       - Setup environment files"
	@echo ""

setup: env-setup install docker-up
	@echo "✅ Environment setup complete"
	@echo "   Services available at:"
	@echo "   - API: http://localhost:3000"
	@echo "   - Redis: localhost:6379"
	@echo "   - PostgreSQL: localhost:5432"
	@echo "   - Elasticsearch: http://localhost:9200"
	@echo "   - Kibana: http://localhost:5601"

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	cd frontends/dashboard-fe && npm install
	cd frontends/builder-fe && npm install
	cd frontends/analytics-fe && npm install
	@echo "✅ Dependencies installed"

env-setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env file created from .env.example"; \
		echo "⚠️  Please update .env with your Salesforce credentials"; \
	else \
		echo "✅ .env file already exists"; \
	fi

test: test-backend test-frontend
	@echo "✅ All tests completed"

test-backend:
	@echo "🧪 Running backend tests..."
	@for service in api-gateway auth-service mcp-client report-service logging-service; do \
		echo "--- $$service ---"; \
		cd services/$$service && python -m pytest tests/ -q --tb=short; \
		cd ../..; \
	done
	@echo "--- integration ---"
	python -m pytest tests/integration/ -q --tb=short

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontends/dashboard-fe && npm run test
	cd frontends/builder-fe && npm run test
	cd frontends/analytics-fe && npm run test

lint: lint-backend lint-frontend
	@echo "✅ Linting completed"

lint-backend:
	@echo "🔍 Linting backend code..."
	pylint services/ || true

lint-frontend:
	@echo "🔍 Linting frontend code..."
	cd frontends/dashboard-fe && npm run lint || true
	cd frontends/builder-fe && npm run lint || true
	cd frontends/analytics-fe && npm run lint || true

docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "✅ Docker services started"
	@sleep 10
	@echo "📊 Services health check..."
	@docker-compose ps

docker-down:
	@echo "🐳 Stopping Docker services..."
	docker-compose down
	@echo "✅ Docker services stopped"

docker-logs:
	docker-compose logs -f

k8s-setup:
	@echo "☸️  Setting up Kubernetes namespace..."
	kubectl apply -f infra/kubernetes/namespace.yaml
	@echo "✅ Namespace created"
	@echo ""
	@echo "📦 Deploying infrastructure services..."
	kubectl apply -f infra/kubernetes/deployments/redis-deployment.yaml
	kubectl apply -f infra/kubernetes/deployments/postgres-deployment.yaml
	kubectl apply -f infra/kubernetes/deployments/elasticsearch-deployment.yaml
	kubectl apply -f infra/kubernetes/deployments/kibana-deployment.yaml
	@echo "✅ Infrastructure services deployed"
	@echo ""
	@echo "🌐 Configuring Ingress..."
	kubectl apply -f infra/kubernetes/ingress.yaml
	@echo "✅ Ingress configured"
	@echo ""
	@echo "⏳ Waiting for services to be ready..."
	kubectl wait --for=condition=available --timeout=300s \
		deployment/redis deployment/postgres deployment/elasticsearch deployment/kibana \
		-n salesforce-reports
	@echo "✅ Kubernetes infrastructure ready"

k8s-deploy: k8s-setup
	@echo "☸️  Deploying API Gateway..."
	kubectl apply -f infra/kubernetes/deployments/api-gateway-deployment.yaml
	@echo "✅ API Gateway deployed"
	@echo ""
	@echo "✅ Kubernetes deployment complete"
	@echo "   Access Kibana at: kubectl port-forward svc/kibana 5601:5601 -n salesforce-reports"

k8s-down:
	@echo "☸️  Removing Kubernetes resources..."
	kubectl delete namespace salesforce-reports --ignore-not-found
	@echo "✅ Kubernetes resources removed"

k8s-logs:
	@echo "Available services:"
	@kubectl get pods -n salesforce-reports
	@echo ""
	@echo "View logs for a service: kubectl logs -f <pod-name> -n salesforce-reports"

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	@echo "✅ Cleanup complete"
