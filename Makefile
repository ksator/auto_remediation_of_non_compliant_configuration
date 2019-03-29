up:
	@echo "======================================================================"
	@echo "Build SaltStack configuration files from template"
	@echo "======================================================================"
	python generate_saltstack_configuration.py
	ls saltstack_configuration -l
	@echo "======================================================================"
	@echo "Start all containers"
	@echo "======================================================================"
	docker-compose up -d
	@echo "======================================================================"
	@echo "Start SaltStack daemons"
	@echo "======================================================================"
	python start_saltstack.py

down:
	@echo "======================================================================"
	@echo "stop docker containers, remove docker containers, remove docker networks"
	@echo "======================================================================"
	docker-compose -f ./docker-compose.yml down

master-cli:
	@echo "======================================================================"
	@echo "start a shell session in the saltstack master container"
	@echo "======================================================================"
	docker exec -i -t master bash

minion-cli:
	@echo "======================================================================"
	@echo "start a shell session in the saltstack minion container"
	@echo "======================================================================"
	docker exec -i -t minion1 bash


