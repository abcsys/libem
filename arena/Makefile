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

.PHONY: docker-up docker-down
docker-up:
	docker compose up --build -d
docker-down:
	docker compose down

.PHONY: kuber-up kuber-down
kuber-up:
	kubectl apply -f arena.yaml
kuber-down:
	kubectl delete -f arena.yaml
