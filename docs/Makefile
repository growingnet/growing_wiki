SPHINXBUILD ?= sphinx-build
SPHINXAUTOBUILD ?= sphinx-autobuild
SOURCEDIR = .
BUILDDIR = _build

.PHONY: figures html stricthtml livehtml clean

figures:
	../scripts/build_figures.sh

html: figures
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

stricthtml: figures
	$(SPHINXBUILD) -W --keep-going -E -a -b html $(SOURCEDIR) $(BUILDDIR)/html

livehtml: figures
	$(SPHINXAUTOBUILD) $(SOURCEDIR) $(BUILDDIR)/html

clean:
	rm -rf $(BUILDDIR)
