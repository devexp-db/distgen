PYTHON = `which python2`

all:
	@echo no build make rule yet, just '"make check"'

check:
	@cd tests/ && PYTHON=${PYTHON} ./testsuite
