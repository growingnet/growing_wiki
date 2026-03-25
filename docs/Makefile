SPHINXBUILD ?= sphinx-build
SPHINXAUTOBUILD ?= sphinx-autobuild
SOURCEDIR = .
BUILDDIR = _build

.PHONY: html livehtml clean

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

livehtml:
	$(SPHINXAUTOBUILD) $(SOURCEDIR) $(BUILDDIR)/html

clean:
	rm -rf $(BUILDDIR)
