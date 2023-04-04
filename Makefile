.PHONY: docs clean

COMMAND = docker-compose exec web python manage.py
PRODUCTION_COMMAND = docker-compose -f docker-compose.prod.yml exec web python manage.py

all: build run collectstatic database-setup

build:
	docker-compose build

create-super-user:
	$(COMMAND) createsuperuser
run:
	docker-compose up -d

run-build:
	docker-compose up -d --build

down:
	docker-compose down

database-initial-migrations:
	$(COMMAND) makemigrations users
	$(COMMAND) makemigrations shop
	$(COMMAND) migrate

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
	docker pull --platform linux/amd64 nginx:latest
	docker-compose down
	docker-compose build
	docker-compose up -d
