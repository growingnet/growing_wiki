SPHINXBUILD ?= sphinx-build
SPHINXAUTOBUILD ?= sphinx-autobuild
SOURCEDIR = .
BUILDDIR = _build

.PHONY: html stricthtml livehtml clean

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

stricthtml:
	$(SPHINXBUILD) -W --keep-going -E -a -b html $(SOURCEDIR) $(BUILDDIR)/html

livehtml:
	$(SPHINXAUTOBUILD) $(SOURCEDIR) $(BUILDDIR)/html

clean:
	rm -rf $(BUILDDIR)
