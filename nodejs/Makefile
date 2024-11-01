# Try to keep the make targets below in sync with the other Makefiles in this repo.

# Run the unit tests
tests:
	jest

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

# Run the linter to verify the code.
lint:
	DEBUG=eslint:cli-engine yarn run eslint src scripts

# Run the linter to verify the code and fix any issues.
lint-fix:
	yarn run eslint --fix --format summary-chart src scripts

# Run this command after changing the help text for a script,
# so that the usage.md file is updated.
# Note: The line length of the resulting README file depends
# on the width of the terminal used to run this command.
help-doc:
	../common/scripts/help_doc_generator ./README.md
