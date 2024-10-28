.PHONY: build
build:
ifndef app
	docker build -f app/Dockerfile .
else
	docker build -t $(app) -f app/Dockerfile .
	docker push $(app)
endif
ifndef serve
	docker build -f serve/Dockerfile .
else
	docker build -t $(serve) -f serve/Dockerfile .
	docker push $(serve)
endif

.PHONY: up down delete
up:
	kubectl apply -f mysql
	kubectl apply -f arena.yaml
down:
	kubectl delete -f arena.yaml
delete:
	kubectl delete -f mysql
	kubectl delete -f arena.yaml
