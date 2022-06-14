lint:
	shellcheck scripts/*.sh scripts/*/*.sh

lint-fix:
	shellcheck --format diff scripts/*.sh scripts/*/*.sh | git apply
