# Makefile for deleting SQLite database, __pycache__, .pytest_cache, and running uvicorn

# Variables
DB_NAME = database

# Targets and Rules
.PHONY: clean_db clean_cache run_app run_unit_tests run_integration_tests

clean_db:
	@echo "Deleting SQLite database..."
	@rm -f $(DB_NAME)*

clean_cache:
	@echo "Deleting __pycache__ directories and .pytest_cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .pytest_cache

clean_all: clean_db clean_cache

run_app: clean_db clean_cache
	@echo "Running uvicorn..."
	@uvicorn app:app --reload

run_unit_tests: clean_all
	pytest -m "not integration_test and not end2end_test"

run_integration_tests: clean_all
	ENVIRONMENT=test python tests/populate_test_db.py
	pytest -m integration_test -vv
	rm database_test.sqlite
	unset ENVIRONMENT

run_end2end_tests:
	ENVIRONMENT=test python tests/populate_test_db.py
	pytest -m end2end_test -vv
	unset ENVIRONMENT