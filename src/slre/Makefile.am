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

if ENABLED_BENCHMARK_SLRE

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS       = slre
noinst_LTLIBRARIES = libslre.la

slre_SOURCES       =
libslre_la_SOURCES = libslre.c slre.h

slre_LDADD         = $(DUMMY_CRT0) \
                     $(top_builddir)/support/libsupport.la \
                     libslre.la \
                     $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)



endif
