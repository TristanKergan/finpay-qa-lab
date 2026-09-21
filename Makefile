.PHONY: help install seed run run-backend run-frontend test-api test-ui test-db test-integration test-security test-all allure-generate allure-serve perf-smoke perf-load docker-up docker-down lint

VENV_BIN = .venv/bin
PYTHON = $(VENV_BIN)/python
PYTEST = $(VENV_BIN)/pytest

help:
	@echo "======================================================================="
	@echo "FinPay QA Lab - Developer & QA Automation Command Center"
	@echo "======================================================================="
	@echo "  make install         Install backend, frontend, and test dependencies"
	@echo "  make seed            Seed database with 5 test personas & transactions"
	@echo "  make run             Run backend and frontend servers concurrently"
	@echo "  make test-api        Execute API test suite with Allure"
	@echo "  make test-ui         Execute Playwright UI test suite"
	@echo "  make test-db         Execute Direct SQL & Database integrity tests"
	@echo "  make test-integration Execute E2E and BUG_MODE defect tests"
	@echo "  make test-security   Execute Security, IDOR, & Injection tests"
	@echo "  make test-all        Execute entire test suite across all levels"
	@echo "  make allure-generate Generate static Allure HTML report"
	@echo "  make allure-serve    Open Allure HTML report in local browser"
	@echo "  make perf-smoke      Run k6 performance smoke test"
	@echo "  make docker-up       Build and run full stack via Docker Compose"
	@echo "  make docker-down     Stop and clean Docker Compose containers"
	@echo "======================================================================="

install:
	uv pip install -r backend/requirements.txt -r tests/requirements.txt
	$(VENV_BIN)/playwright install chromium
	cd frontend && npm install

seed:
	PYTHONPATH=. $(PYTHON) backend/scripts/seed_data.py

run-backend:
	PYTHONPATH=. $(VENV_BIN)/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev -- --port 3000 --host 0.0.0.0

run:
	@echo "Starting FinPay backend and frontend..."
	@make -j 2 run-backend run-frontend

test-api:
	PYTHONPATH=. $(PYTEST) tests/api -v --alluredir=allure-results

test-ui:
	PYTHONPATH=. $(PYTEST) tests/ui -v --alluredir=allure-results

test-db:
	PYTHONPATH=. $(PYTEST) tests/database -v --alluredir=allure-results

test-integration:
	PYTHONPATH=. $(PYTEST) tests/integration -v --alluredir=allure-results

test-security:
	PYTHONPATH=. $(PYTEST) tests/security -v --alluredir=allure-results

test-all:
	PYTHONPATH=. $(PYTEST) tests/ -v --alluredir=allure-results

allure-generate:
	npx allure generate allure-results -o allure-report --clean

allure-serve:
	npx allure open allure-report

perf-smoke:
	k6 run tests/performance/k6-smoke.js || docker run --rm -i --network="host" -v $$(pwd)/tests/performance:/perf grafana/k6 run /perf/k6-smoke.js

perf-load:
	k6 run tests/performance/k6-load.js || docker run --rm -i --network="host" -v $$(pwd)/tests/performance:/perf grafana/k6 run /perf/k6-load.js

lint:
	$(VENV_BIN)/ruff check backend tests
	cd frontend && npm run build

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v
