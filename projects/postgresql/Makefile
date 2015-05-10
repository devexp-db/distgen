dist = fedora
distver = 21

Dockerfile: postgresql.yaml project.py
	dg --distro $(dist)-$(distver)-x86_64.yaml  --instantiate $< docker.tpl > $@
