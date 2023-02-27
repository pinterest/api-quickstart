tests:
	jest

e2e_setup:
	@echo end to end tests set up...
	../common/scripts/e2e_tests_prerequisites

e2e_tests: e2e_setup
	@echo end to end tests...
	../common/scripts/e2e_tests_read
	../common/scripts/e2e_tests_write
	../common/scripts/e2e_tests_ads

lint:
	DEBUG=eslint:cli-engine yarn run eslint src scripts

lint-fix:
	yarn run eslint --fix --format summary-chart src scripts

# Run this command after changing the help text for a script,
# so that the usage.md file is updated.
help-doc:
	../common/scripts/help_doc_generator ./README.md
