unit_tests:
	@echo generic unit tests...
	nosetests --rednose ./tests/src
	@echo v3 unit tests...
	nosetests --rednose ./tests/src/v3

integration_tests:
	@echo integration tests...
	nosetests --rednose ./tests/scripts

tests: unit_tests integration_tests
