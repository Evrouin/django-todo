.PHONY: help install migrate run test lint format clean docker-up docker-down check

help:
	@echo "Django Auth - Available Commands"
	@echo "================================="
	@echo "install       - Install dependencies"
	@echo "migrate       - Run database migrations"
	@echo "run           - Run development server"
	@echo "test          - Run tests with coverage"
	@echo "lint          - Run all linting checks"
	@echo "format        - Auto-format code"
	@echo "check         - Run all code quality checks"
	@echo "clean         - Remove cache and build files"
	@echo "docker-up     - Start Docker containers"
	@echo "docker-down   - Stop Docker containers"
	@echo "docker-logs   - View Docker logs"

install:
	pip install -r requirements/development.txt

migrate:
	python manage.py migrate

run:
	python manage.py runserver

test:
	pytest --cov=apps --cov-report=html --cov-report=term

lint:
	@echo "Running Flake8..."
	flake8 apps/ config/
	@echo "Running Ruff..."
	ruff check apps/ config/

format:
	@echo "Formatting with Black..."
	black apps/ config/
	@echo "Auto-fixing with Ruff..."
	ruff check --fix apps/ config/
	@echo "Sorting imports..."
	ruff check --select I --fix apps/ config/

check:
	@echo "Running all code quality checks..."
	./scripts/check_code.sh

typecheck:
	mypy apps/ config/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f web

docker-test:
	docker-compose exec web pytest -v

docker-format:
	docker-compose exec web black apps/ config/
	docker-compose exec web ruff check --fix apps/ config/

docker-lint:
	docker-compose exec web flake8 apps/ config/
	docker-compose exec web ruff check apps/ config/
	docker-compose exec web mypy apps/ config/
