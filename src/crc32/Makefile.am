# Makefile.am for BEEBS CRC32 test
#
# Copyright (C) 2013 Embecosm Limited and University of Bristol
#
# Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_CRC32

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS        = crc32
noinst_LTLIBRARIES  = libcrc32.la

crc32_SOURCES       =

libcrc32_la_SOURCES = crc_32.c

crc32_LDADD         = $(DUMMY_CRT0) \
                      $(top_builddir)/support/libsupport.la \
                      libcrc32.la \
                      $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)

endif
