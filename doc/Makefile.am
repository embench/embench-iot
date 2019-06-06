# Makefile.am -- Documentation automake configuration file
#
# Copyright (C) 2009, 2013, 2019 Embecosm Limited
#
# Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.
#
# SPDX-License-Identifier: GPL-3.0-or-later

ROOT = README
SRC = $(srcdir)/$(ROOT).adoc
SRC_STRIPPED = $(builddir)/$(ROOT)-stripped.adoc

.PHONY: pdf-local
pdf-local: $(builddir)/$(ROOT).pdf

$(builddir)/$(ROOT).pdf: sanity-check $(SRC)
	asciidoctor-pdf -d article $(SRC) -o $@

.PHONY: install-pdf-local
install-pdf-local: $(builddir)/$(ROOT).pdf
	install -t $(docdir) $^

.PHONY: html-local
html-local: $(builddir)/$(ROOT).html

$(builddir)/$(ROOT).html: sanity-check $(SRC)
	asciidoctor -d article -b html $(SRC) -o $@

.PHONY: install-html-local
install-html-local: $(builddir)/$(ROOT).html
	install -t $(docdir) $^

# It is all too easy for the document history and title page to have diverging
# version numbers.  This target checks first.

.PHONY: sanity-check
sanity-check:
	@s=$$(sed -n < $(SRC) -e '3s/Issue //p') ; \
	t=$$(sed -n < $(SRC) -e "/== Document history/,/^$$/p" | \
	           grep -c "$${s}") ; \
	if [ $${t} -ne 1 ] ; \
	then \
	    echo "Version number of title and document history do not match" ; \
	    exit 1 ; \
	fi

$(builddir)/custom.dict: $(srcdir)/custom.wordlist
	aspell --lang=en create master ./$@ < $<

.PHONY: spell-local
spell-local: $(builddir)/custom.dict $(SRC)
	sed < $(SRC) > $(SRC_STRIPPED) -e 's/`[^`]\+`//gp' \
	    -e '/^----$$/,/^----$$/d'
	aspell --master=en_US --mode=none --add-extra-dicts=./custom.dict \
	    -c $(SRC_STRIPPED)
	$(RM) $(SRC_STRIPPED)

clean-local:
	$(RM) $(ROOT)-stripped.adoc $(ROOT).pdf $(ROOT).html \
	      $(builddir)/custom.dict
