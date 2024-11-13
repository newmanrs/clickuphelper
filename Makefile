.PHONY: clean build deploy test venv

venv:
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install build twine pytest wheel
	. venv/bin/activate && pip install -e ".[dev]"

clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	. venv/bin/activate && python -m build

test:
	. venv/bin/activate && python -m pytest tests/

# Deploy to test PyPI
deploy-test: build
	. venv/bin/activate && python -m twine upload --repository testpypi dist/*

# Deploy to production PyPI
deploy: build
	. venv/bin/activate && python -m twine upload dist/*

# Install development dependencies (if you already have a venv activated)
dev-setup:
	pip install --upgrade pip
	pip install build twine pytest wheel
	pip install -e ".[dev]"
