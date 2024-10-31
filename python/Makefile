# Unit tests check each module in isolation.
unit_tests:
	@echo generic unit tests...
	python -m pytest ./tests/src

# These tests verify the scripts, and do not have external dependencies.
integration_tests:
	@echo integration tests...
	python -m pytest ./tests/scripts

# Try to keep the make targets below in sync with the other Makefiles in this repo.

# Verify that the prerequisites for the end-to-end tests are met.
e2e_setup:
	@echo end to end tests set up...
	../common/scripts/e2e_tests_prerequisites

# Run the end-to-end tests.
e2e_tests: e2e_setup
	@echo end to end tests...
	../common/scripts/e2e_tests_read
	../common/scripts/e2e_tests_write
	../common/scripts/e2e_tests_ads

# Run the unit and integration tests. Neither have external dependencies
tests: unit_tests integration_tests

# Run the linter to verify the code.
# flake8 configuration is in the .flake8 file.
# black and isort configurations are in the pyproject.toml file.
lint:
	black --check .
	isort --profile black --check .
	flake8 --quiet --statistics

# Run the linter to verify the code and fix any issues.
lint-fix:
	black src scripts tests
	isort --profile black .
	flake8

# Run this command after changing the help text for a script,
# so that the usage.md file is updated.
# Note: The line length of the resulting README file depends
# on the width of the terminal used to run this command.
help-doc:
	../common/scripts/help_doc_generator ./README.md
