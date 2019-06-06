# Makefile.am for building a BEEBS benchmark
#
# Copyright (C) 2013 Embecosm Limited and University of Bristol
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# Contributor: James Pallister <james.pallister@bristol.ac.uk>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_AHA_MONT64

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS             = aha-mont64
noinst_LTLIBRARIES       = libaha-mont64.la

aha_mont64_SOURCES       =

libaha_mont64_la_SOURCES = mont64.c

aha_mont64_LDADD         = $(DUMMY_CRT0) \
                           $(top_builddir)/support/libsupport.la \
                           libaha-mont64.la \
                           $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)

endif
