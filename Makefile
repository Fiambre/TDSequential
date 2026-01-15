.PHONY: help install install-dev test test-cov test-fast clean lint format

help:
	@echo "Comandos disponibles:"
	@echo "  make install      - Instalar el paquete"
	@echo "  make install-dev  - Instalar con dependencias de desarrollo"
	@echo "  make test         - Ejecutar todos los tests"
	@echo "  make test-cov     - Ejecutar tests con cobertura"
	@echo "  make test-fast    - Ejecutar tests en paralelo"
	@echo "  lint             - Verificar estilo de código"
	@echo "  format           - Formatear código con black e isort"
	@echo "  clean            - Limpiar archivos temporales"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-verbose:
	pytest -v

test-coverage:
	pytest --cov=tdsequential --cov-report=html --cov-report=term-missing

test-watch:
	pytest-watch

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: test coverage clean install-dev
