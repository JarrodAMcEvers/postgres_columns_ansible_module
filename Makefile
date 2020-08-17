test:
	python -m unittest discover tests

up:
	docker-compose up -d
down:
	docker-compose down
