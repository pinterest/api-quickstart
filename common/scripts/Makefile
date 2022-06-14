# These files are sourced by the other scripts, have no shebang and therefore
# need the shell to be specified.
SHELLCHECK_SOURCES=--shell bash api_app_credentials.template api_env e2e_tests_preamble

# These files are scripts that (may) source the above files.
# SC2059 prevents variables in printf. Fixing this info-level
# message would make the code less clear.
SHELLCHECK_SCRIPTS=--exclude SC2059 --external-sources e2e_tests_prerequisites e2e_tests_read e2e_tests_write e2e_tests_ads help_doc_generator

lint:
	shellcheck $(SHELLCHECK_SOURCES)
	shellcheck $(SHELLCHECK_SCRIPTS)

# Empty input causes "git apply" to terminate with "error: unrecognized input" and a non-zero exit code.
# So, run the lint fixer if there is something to fix.
lint-fix:
	shellcheck $(SHELLCHECK_SOURCES) > /dev/null || shellcheck --format diff $(SHELLCHECK_SOURCES) | git apply
	shellcheck $(SHELLCHECK_SCRIPTS) > /dev/null || shellcheck --format diff $(SHELLCHECK_SCRIPTS) | git apply
