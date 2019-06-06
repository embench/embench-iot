# Makefile.am for building a BEEBS benchmark
#
# Copyright (C) 2013-2014 Embecosm Limited and University of Bristol
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# Contributor: James Pallister <james.pallister@bristol.ac.uk>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_MATMULT_INT

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS               = matmult-int
noinst_LTLIBRARIES         = libmatmult-int.la

matmult_int_SOURCES        =

libmatmult_int_la_SOURCES  = matmult-int.c

matmult_int_LDADD          = $(DUMMY_CRT0) \
                             $(top_builddir)/support/libsupport.la \
                             libmatmult-int.la \
                             $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)

libmatmult_int_la_CPPFLAGS = -DMATMULT_INT ${AM_CPPFLAGS}

endif
