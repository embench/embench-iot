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

if ENABLED_BENCHMARK_STATEMATE

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS            = statemate
noinst_LTLIBRARIES      = libstatemate.la

statemate_SOURCES       =
libstatemate_la_SOURCES = libstatemate.c

statemate_LDADD         = $(DUMMY_CRT0) \
                          $(top_builddir)/support/libsupport.la \
                          libstatemate.la \
                          $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)



endif
