.PHONY: dist cli install
dist:
	python setup.py sdist bdist_wheel && twine upload --skip-existing dist/*
	rm -rf build dist *.egg-info
install:
	pip install -e .
	mkdir -p ~/.libem && touch ~/.libem/config.yaml
uninstall:
	pip uninstall libem -y && rm -r libem.egg-info || true

# match examples
.PHONY: run match browse chat all
run: match
match:
	python examples/match.py
browse:
	python examples/tool/browse.py
chat:
	python examples/tool/chat.py
block:
	python examples/block.py
all: match match-local browse chat

# extract examples
.PHONY: extract
extract:
	python examples/extract.py

# tuning examples
.PHONY: rule shot tune
rule:
	python examples/tune/rule_from_mistakes.py
shot:
	python examples/tune/similar_shots.py
tune: rule

# optimize examples
.PHONY: profile prompt_batch async_request async_batch batch
profile:
	python examples/optimize/profile.py
prompt_batch:
	python examples/optimize/prompt_batch.py
async_request:
	python examples/optimize/async_request.py
async_batch:
	python examples/optimize/async_batch.py
batch: async_batch

# opensource model examples
.PHONY: mlx_lm llama local
mlx_lm:
	pip install mlx_lm
llama:
	python examples/model/llama.py
local: llama

# benchmarks
.PHONY: benchmark analyze plot
benchmark:
	python -m benchmark.run
analyze:
	python -m benchmark.analyze -m
plot:
	python -m benchmark.plot

# tests clean
.PHONY: test clean
test:
	pytest -v test/*
clean:
	rm -r logs > /dev/null 2>&1 || true

# refresh price
.PHONY: price
price:
	python -c "from libem import optimize; optimize.refresh_price_cache()"

# download sample data
.PHONY: data
data:
	git clone https://github.com/abcsys/libem-sample-data.git ../libem-sample-data

# libem serve
.PHONY: serve build
serve:
	python -m serve.run
build:
	docker build -t silveryfu/libem-serve:0.0.17 -f serve/deploy/Dockerfile . && \
	docker push silveryfu/libem-serve:0.0.17
