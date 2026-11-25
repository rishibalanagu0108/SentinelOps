.PHONY: start status verify logs stop

start:
	docker compose up --build --detach --wait --wait-timeout 300

status:
	docker compose ps

verify:
	python3 scripts/verify_stack.py

logs:
	docker compose logs --follow

stop:
	docker compose down --remove-orphans
