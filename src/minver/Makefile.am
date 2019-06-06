# Makefile.am for building a BEEBS benchmark
#
# Copyright (C) 2014 Embecosm Limited and University of Bristol
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# Contributor: Pierre Langlois <pierre.langlois@embecosm.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_MINVER

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS         = minver
noinst_LTLIBRARIES   = libminver.la

minver_SOURCES       =
libminver_la_SOURCES = libminver.c

minver_LDADD         = $(DUMMY_CRT0) \
                       $(top_builddir)/support/libsupport.la \
                       libminver.la \
                       $(top_builddir)/support/libbeebsc.la \
                       $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT) \
                       $(LIBM)



endif
