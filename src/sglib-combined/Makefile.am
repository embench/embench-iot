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

if ENABLED_BENCHMARK_SGLIB_COMBINED

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS                  = sglib-combined
noinst_LTLIBRARIES            = libsglib-combined.la

sglib_combined_SOURCES        =

libsglib_combined_la_SOURCES  = combined.c sglib.h
libsglib_combined_la_CPPFLAGS = -DQUICK_SORT ${AM_CPPFLAGS}

sglib_combined_LDADD          = $(DUMMY_CRT0) \
                                $(top_builddir)/support/libsupport.la \
                                libsglib-combined.la \
                                $(top_builddir)/support/libbeebsc.la \
                                $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)

endif
