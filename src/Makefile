run_unit_tests:
	pytest -m "not integration_test"

run_integration_tests:
	ENVIRONMENT=test python tests/populate_test_db.py
	pytest -m integration_test -vv
	rm database_test.sqlite
	unset ENVIRONMENT