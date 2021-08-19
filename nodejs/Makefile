tests:
	jest

lint:
	DEBUG=eslint:cli-engine yarn run eslint src scripts

# fails when there are no errors
lint-summary:
	yarn run eslint --format summary-chart src scripts

lint-fix:
	yarn run eslint --fix src scripts
