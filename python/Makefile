unit_tests:
	@echo generic unit tests...
	python -m pytest ./tests/src

integration_tests:
	@echo integration tests...
	python -m pytest ./tests/scripts

e2e_setup:
	@echo end to end tests set up...
	../common/scripts/e2e_tests_prerequisites

e2e_tests: e2e_setup
	@echo end to end tests...
	../common/scripts/e2e_tests_read
	../common/scripts/e2e_tests_write
	../common/scripts/e2e_tests_ads

tests: unit_tests integration_tests

# flake8 configuration is in the .flake8 file.
# black and isort configurations are in the pyproject.toml file.
lint:
	black --check .
	isort --profile black --check .
	flake8 --quiet --statistics

lint-fix:
	black src scripts tests
	isort --profile black .
	flake8

# Run this command after changing the help text for a script,
# so that the usage.md file is updated.
help-doc:
	../common/scripts/help_doc_generator ./README.md
