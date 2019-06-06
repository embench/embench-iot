# Makefile.am for BEEBS cubic test
#
# Copyright (C) 2013 Embecosm Limited and University of Bristol
#
# Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_CUBIC

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS        = cubic
noinst_LTLIBRARIES  = libcubic.la

cubic_SOURCES       =

libcubic_la_SOURCES = libcubic.c basicmath_small.c pi.h snipmath.h sniptype.h

cubic_LDADD         = $(DUMMY_CRT0) \
                      $(top_builddir)/support/libsupport.la \
                      libcubic.la \
                      $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT) \
                      $(LIBM)
endif
