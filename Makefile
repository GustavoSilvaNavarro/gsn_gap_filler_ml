#!make
PORT = 8080
SERVICE_NAME = gap_filler_service
CONTAINER_NAME = $(SERVICE_NAME)
DOCKER_COMPOSE_TAG = $(SERVICE_NAME)_1
APP_PYFILES=app/
TESTS_PYFILES=tests/
PYFILES = $(APP_PYFILES)
PYTHON_VERSION=3.13

# UV
setup-venv:
	uv venv .venv

install-uv:
	uv pip install -r requirements.txt

install-dev-uv:
	uv pip install -r requirements_dev.txt

# hooks
setup-git-hooks:
	@echo "\n👻 Setting up pre commit hook to maintain code quality"
	pre-commit install

# Virtual env
venv:
	@echo "\n🐍 Creating virtual environment..."
	python -m venv .venv

activate-venv:
	@echo "\n 🐍 Activating virtual environment..."
	source .venv/bin/activate

# Install
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements_dev.txt

# DB operations
# Sync migrations
setup-alembic:
	alembic init migrations

# Async migrations
async-alembic:
	alembic init -t async migrations

migrate:
	set -a; . ./.dev.env; alembic revision --autogenerate -m "$(filename)"

upgrade:
	@set -a; . ./.dev.env; alembic upgrade head

downgrade:
	set -a; . ./.dev.env; alembic downgrade $(version)

head:
	set -a; . ./.dev.env; alembic current

# Runs the static code analysis tools
.PHONY: lint
lint:
	@ruff check --fix ${PYFILES}
	@mypy --config-file pyproject.toml ${PYFILES}

# Formats the code using black and isort
.PHONY: format
format:
	@find ${PYFILES} -name "*.py" ! -name "test_*.py" -exec docformatter -i {} +
	@ruff format ${PYFILES}

# Checks if the code is formatted correctly
.PHONY: check
check:
	@find "${PYFILES}" -name "test_*.py" -exec docformatter -c {} +
	@ruff format --check ${PYFILES}
	@ruff check ${PYFILES}

# Local Start up
dev: upgrade
	uvicorn app:app --reload --proxy-headers --host 0.0.0.0 --port ${PORT}

start: upgrades
	uvicorn app:app --proxy-headers --host 0.0.0.0 --port ${PORT}

# Docker command
run-external-services:
	docker compose -f ./docker-compose.inf.yml up -d db redis redis-sentinel

down-rm:
	docker compose -f ./docker-compose.inf.yml down --remove-orphans --rmi all --volumes

# Infrastructure to support project
infra-up:
	@echo "\n🛫 Building external services needed it for project..."
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose -f ./docker-compose.inf.yml build --parallel
	docker compose -f ./docker-compose.inf.yml up -d --force-recreate
