PROJECT = distgen
PYTHON  := python3
VERSION := $(shell python3 -m distgen --version | grep -o '[0-9]*\.[0-9]*')
RELEASE := 1

git_rev = \
	rev="$$(git rev-parse HEAD)" ; \
	rev_short=$${rev:0:5} ; \
	echo $$rev_short

rpmbuild_options = \
	--define "_sourcedir $(PWD)" \
	--define "_rpmdir $(PWD)" \
	--define "_specdir $(PWD)" \
	--define "_builddir $(PWD)" \
	--define "_srcrpmdir $(PWD)" \
	--define "dist %nil"

tarball = "$(PROJECT)-$(VERSION).tar.gz"

spec = $(PROJECT).spec

all: $(spec) $(tarball)

$(spec): $(PROJECT).spec.dg
	$(PYTHON) -m distgen --template $< \
	    --distro fedora-rawhide-x86_64 \
	    --macro "VERSION $(VERSION)" \
	    --macro "RELEASE $(RELEASE)" \
	    --output $@

$(tarball):
	$(PYTHON) -m build -o . ..

srpm: $(spec) $(tarball)
	rm -rf *.src.rpm
	rpmbuild -bs $(rpmbuild_options) $(spec)

rpm: srpm
	rpmbuild --rebuild *.src.rpm --define "_rpmdir $(PWD)"


clean:
	rm -rf *.src.rpm *.tar.gz $(PROJECT)-* noarch *.spec
