PYTHON = `which python2`

all:
	@echo no build make rule yet, just '"make check"'

test-end2end:
	@cd tests/ && PYTHON=${PYTHON} ./testsuite

test-unit:
	@cd tests/ && PYTHONPATH=..:$${PYTHONPATH} ${PYTHON} -m pytest unittests/

check: test-unit test-end2end
