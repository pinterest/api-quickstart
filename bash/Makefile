SCRIPTS=scripts/*.sh
lint:
	shellcheck $(SCRIPTS)

# Empty input causes "git apply" to terminate with "error: unrecognized input" and a non-zero exit code.
# So, run the lint fixer if there is something to fix.
lint-fix:
	shellcheck $(SCRIPTS) > /dev/null || shellcheck --format diff $(SCRIPTS) | git apply
