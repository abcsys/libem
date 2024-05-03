.PHONY: dist install
dist:
	python setup.py sdist bdist_wheel && twine upload --skip-existing dist/*
	rm -rf build dist *.egg-info
install:
	pip install -e . && rm -rf *.egg-info
	mkdir -p ~/.libem && touch ~/.libem/config.yaml

.PHONY: run browse
run:
	python examples/match.py
browse:
	python examples/browse.py
