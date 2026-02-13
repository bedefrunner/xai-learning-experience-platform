.PHONY: help up down build rebuild restart logs logs-backend logs-db migrate makemigrations shell prune createsuperuser

help:
	@echo "Available commands:"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make build           - Build and start services"
	@echo "  make rebuild         - Rebuild services from scratch"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - View logs from all services"
	@echo "  make logs-backend    - View logs from backend service"
	@echo "  make logs-db         - View logs from database service"
	@echo "  make migrate         - Run database migrations"
	@echo "  make makemigrations  - Create new migrations"
	@echo "  make shell           - Open Django shell"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make prune           - Remove all Docker resources (clean slate)"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose up --build -d

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-db:
	docker-compose logs -f db

migrate:
	docker-compose exec backend uv run python manage.py migrate

makemigrations:
	docker-compose exec backend uv run python manage.py makemigrations

shell:
	docker-compose exec backend uv run python manage.py shell

createsuperuser:
	docker-compose exec backend uv run python manage.py createsuperuser

prune:
	docker-compose down -v
	docker system prune -af --volumes
