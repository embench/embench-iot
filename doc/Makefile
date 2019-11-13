# Makefile to assist Embench documentation

# Copyright (C) 2019 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

# Generate a table of contents

.PHONY: toc
toc: README.md
	./gentoc.sh

# Spell check the documentation

.PHONY: spell
spell: README.md
	echo "Spell checking not yet implemented."

# PDF version of the documentation

.phony: pdf
pdf: README.pdf

README.pdf: README.md
	pandoc -o $@ $^

# HTML version of the documentation

.phony: html
html: README.html

README.html: README.md
	pandoc -o $@ $^

# Clean up intermediate files

.phony: clean
clean:
	$(RM) README.pdf
	$(RM) README.html
	$(RM) README.md.old
