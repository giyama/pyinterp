.PHONY: clean test audit cov

clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -name "*.pyc" -delete

test:
	pytest

audit:
	python -m "pylama.main"

cov:
	pytest --cov=. 
