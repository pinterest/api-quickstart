unit_tests:
	@echo generic unit tests...
	nosetests --rednose ./tests/src
	@echo v3 unit tests...
	nosetests --rednose ./tests/src/v3
	@echo v5 unit tests...
	nosetests --rednose ./tests/src/v5

integration_tests:
	@echo integration tests...
	nosetests --rednose ./tests/scripts

tests: unit_tests integration_tests

# Note: flake8 configuration is in .flake8 file.
lint_check:
	black --check src scripts tests
	isort --profile black --check src scripts tests
	flake8 --quiet --statistics

lint:
	black src scripts tests
	isort --profile black src scripts tests
	flake8

