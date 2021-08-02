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

# flake8 configuration is in the .flake8 file.
# black and isort configurations are in the pyproject.toml file.
lint_check:
	black --check .
	isort --profile black --check .
	flake8 --quiet --statistics

lint:
	black src scripts tests
	isort --profile black .
	flake8

