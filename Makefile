.PHONY: help setup install test lint docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make setup           - Setup local environment"
	@echo "  make install         - Install dependencies"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linters"
	@echo "  make docker-up       - Start Docker services"
	@echo "  make docker-down     - Stop Docker services"

setup: install docker-up
	@echo "✅ Environment setup complete"

install:
	pip install -r requirements.txt
	cd frontends/dashboard-fe && npm install
	cd frontends/builder-fe && npm install
	cd frontends/analytics-fe && npm install

test:
	pytest services/ -v --cov=services/

lint:
	pylint services/
	eslint frontends/

docker-up:
	docker-compose -f infra/docker-compose.yml up -d

docker-down:
	docker-compose -f infra/docker-compose.yml down
