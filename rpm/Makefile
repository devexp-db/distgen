project = distgen

project_version = \
	cd .. ; \
	python setup.py --version

generate_tarball = \
	cd .. ; \
	python setup.py sdist --owner=root --group=root --dist-dir rpm

git_rev = \
	rev="$$(git rev-parse HEAD)" ; \
	rev_short=$${rev:0:5} ; \
	echo $$rev_short

rpmdif_options = \
	--define "_sourcedir $(PWD)" \
	--define "_rpmdir $(PWD)" \
	--define "_specdir $(PWD)" \
	--define "_builddir $(PWD)" \
	--define "_srcrpmdir $(PWD)"

tarball = "$(project)-$(shell $(project_version)).tar.gz"

spec = $(project).spec

all: srpm

$(tarball): clean
	$(generate_tarball)

spec_check:
	test '$(shell $(git_rev))' = '$(shell cat $(spec) | grep "gitrev " | cut -d' ' -f3 )'

srpm: $(tarball) spec_check
	rm -rf *.src.rpm
	rpmbuild -bs $(rpmdif_options) $(spec)

rpm: srpm
	rpmbuild --rebuild *.src.rpm --define "_rpmdir $(PWD)"


clean:
	rm -rf *.src.rpm *.tar.gz $(project)-*
