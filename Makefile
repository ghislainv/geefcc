# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -E
SPHINXBUILD   ?= ~/venvs/geefcc/bin/sphinx-build
SOURCEDIR     = docsrc
BUILDDIR      = build

EMACS_INIT = ~/.config/emacs/init.el

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile org github

# Execute make org locally to convert org file to rst
# Not done on GitHub CI
org:
	@echo "Exporting org notebooks to rst..."
	@find $(SOURCEDIR)/notebooks -name "*.org" \
		-not -name "*_*yr.org" \
		-not -name "*_1.org" \
		-not -name "#*" \
		| while read f; do \
			echo "  $$f"; \
			emacs --batch -q \
				-l $(EMACS_INIT) \
				"$$f" \
				-f org-rst-export-to-rst \
				2>/dev/null; \
		done
	@echo "Done."

github:
	@make html
	@cp -a build/html/. ./docs

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) -a $(O)
