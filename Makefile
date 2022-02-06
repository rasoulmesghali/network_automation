.ONESHELL:
SHELL := /bin/bash

build:	
	docker-compose build;

run: build
	docker-compose up;

down:
	docker-compose down;

kompose:
	kompose convert --out k8s;

