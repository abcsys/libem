.PHONY: dist cli install
dist:
	python setup.py sdist bdist_wheel && twine upload --skip-existing dist/*
	rm -rf build dist *.egg-info
install:
	pip install -e .
	mkdir -p ~/.libem && touch ~/.libem/config.yaml
uninstall:
	pip uninstall libem -y && rm -r libem.egg-info || true

# examples
.PHONY: run match no_match browse chat all
run: match
match:
	python examples/match.py
no_match:
	python examples/no_match.py
browse:
	python examples/browse.py
chat:
	python examples/chat.py
all: match no_match browse chat

# tuning examples
.PHONY: tune
tune:
	python examples/tune/rule_from_mistakes.py


# benchmarks
.PHONY: benchmark analyze plot
benchmark:
	python -m benchmark.run -q
analyze:
	python -m benchmark.analyze -m
plot:
	python -m benchmark.plot


# tests clean
.PHONY: test clean
test: all
clean:
	rm -r logs > /dev/null 2>&1 || true

# refresh price
.PHONY: price
price:
	python -c "from libem import optimize; optimize.refresh_price_cache()"
