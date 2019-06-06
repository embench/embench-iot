# Makefile.am for building the nbody benchmark
#
# Copyright (C) 2013 Embecosm Limited and University of Bristol
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# Contributor: James Pallister <james.pallister@bristol.ac.uk>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_NBODY

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS        = nbody
noinst_LTLIBRARIES  = libnbody.la

nbody_SOURCES       =
libnbody_la_SOURCES = nbody.c

nbody_LDADD         = $(DUMMY_CRT0) \
                      $(top_builddir)/support/libsupport.la \
                      libnbody.la \
                      $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT) \
                      $(LIBM)
endif
