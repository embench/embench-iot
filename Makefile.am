# Top level Makefile.am for building a BEEBS benchmark
#
# Copyright (C) 2013 Embecosm Limited and University of Bristol
# Copyright (C) 2018 Embecosm Limited
#
# Contributor: James Pallister <james.pallister@bristol.ac.uk>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# SPDX-License-Identifier: GPL-3.0-or-later

ACLOCAL_AMFLAGS = -I m4

SUBDIRS = doc support src testsuite

EXTRA_DIST= config

# Clean up any test results
distclean-local:
	-rm -fr results/
