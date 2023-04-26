.PHONY: docs clean

COMMAND = docker-compose exec web python manage.py
PRODUCTION_COMMAND = docker-compose -f docker-compose.prod.yml exec web python manage.py
MAC_FILE = docker-compose -f docker-compose-mac.yml
LOCAL = python manage.py
all: build run collectstatic database-setup

build:
	docker-compose build

create-super-user:
	$(COMMAND) createsuperuser

collectstatic:
	$(COMMAND) collectstatic --no-input

run:
	docker-compose up

run-d:
	docker-compose up -d

run-build:
	docker-compose up --build

run-d-build:
	docker-compose up -d --build

down:
	docker-compose down

database-initial-migrations:
	$(COMMAND) makemigrations users
	$(COMMAND) makemigrations shop
	$(COMMAND) makemigrations chat
	$(COMMAND) migrate

local-database-initial-migrations:
	$(COMMAND) makemigrations users
	$(COMMAND) makemigrations shop
	$(COMMAND) makemigrations chat
	$(LOCAL) migrate

database-migrations:
	$(COMMAND) makemigrations
	$(COMMAND) migrate

dockerclean:
	docker system prune -f
	docker system prune -f --volumes

collectstatic:
	$(COMMAND) collectstatic --no-input

logs_web:
	docker-compose logs web

logs_db:
	docker-compose logs db

logs_nginx:
	docker-compose logs nginx

production-build:
	 docker-compose -f docker-compose.prod.yml up -d --build

production-migrate:
	docker-compose -f docker-compose.prod.yml down -v
	docker-compose -f docker-compose.prod.yml up -d --build
	$(PRODUCTION_COMMAND) makemigrations
	$(PRODUCTION_COMMAND) migrate --noinput

mac-m1-build:
	export DOCKER_DEFAULT_PLATFORM=linux/amd64
	docker pull --platform linux/amd64 nginx:latest
	docker pull --platform linux/amd64 postgres:15-alpine
	docker pull --platform linux/amd64 redis:latest
	$(MAC_FILE) down
	$(MAC_FILE) build
	$(MAC_FILE) up

mac-run:
	$(MAC_FILE) up

mac-run-db:
	$(MAC_FILE) up db

mac-restart-web:
	$(MAC_FILE) restart web nginx
