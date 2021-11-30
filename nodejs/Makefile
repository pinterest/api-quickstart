tests:
	jest

lint:
	DEBUG=eslint:cli-engine yarn run eslint src scripts

lint-fix:
	yarn run eslint --fix src scripts

# Run this command after changing the help text for a script,
# so that the usage.md file is updated.
help-doc:
	../common/scripts/help_doc_generator ./README.md
