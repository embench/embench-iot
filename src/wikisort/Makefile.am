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

if ENABLED_BENCHMARK_WIKISORT

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS           = wikisort
noinst_LTLIBRARIES     = libwikisort.la

wikisort_SOURCES       =
libwikisort_la_SOURCES = libwikisort.c

wikisort_LDADD         = $(DUMMY_CRT0) \
                         $(top_builddir)/support/libsupport.la \
                         libwikisort.la \
                         $(top_builddir)/support/libbeebsc.la \
                         $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT) \
                         $(LIBM)

endif
