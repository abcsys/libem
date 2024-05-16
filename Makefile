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
.PHONY: run match unmatch browse chat all
run: match
match:
	python examples/match.py
unmatch:
	python examples/unmatch.py
browse:
	python examples/browse.py
chat:
	python examples/chat.py
all: match unmatch browse chat

# self-refinement examples
.PHONY: learn35 learn4o learn
learn35:
	python examples/learn35.py
learn4o:
	python examples/learn4o.py
learn: learn4o


# benchmarks
.PHONY: product benchmark
benchmark: product
product:
	python benchmark/product.py


# tests clean
.PHONY: test clean
test: all
clean:
	rm -r benchmark/results > /dev/null 2>&1 || true
	rm -r logs > /dev/null 2>&1 || true
