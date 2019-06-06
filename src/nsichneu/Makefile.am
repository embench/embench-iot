# Makefile.am for building a BEEBS benchmark
#
# Copyright (C) 2014 Embecosm Limited and University of Bristol
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# Contributor: James Pallister <james.pallister@bristol.ac.uk>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_NSICHNEU

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS           = nsichneu
noinst_LTLIBRARIES     = libnsichneu.la

nsichneu_SOURCES       =
libnsichneu_la_SOURCES = libnsichneu.c

nsichneu_LDADD         = $(DUMMY_CRT0) \
                         $(top_builddir)/support/libsupport.la \
                         libnsichneu.la \
                         $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)



endif
