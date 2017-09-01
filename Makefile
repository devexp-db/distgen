PYTHON = `which python2`

all:
	@echo no build make rule yet, just '"make check"'

test-end2end:
	@cd tests/ && PYTHON=${PYTHON} ./testsuite

test-unit:
	PYTHONPATH=..:$${PYTHONPATH} ${PYTHON} -m pytest `[ ! -z ${COVERAGE} ] && echo "--cov distgen"` tests/unittests/

check: test-unit test-end2end
