# Makefile.am for nettle-sha256
#
# Copyright (C) 2019 Embecosm Limited and University of Bristol
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# Contributor: Graham Markall <graham.markall@embecosm.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_NETTLE_SHA256

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS             = nettle-sha256
noinst_LTLIBRARIES       = libnettle-sha256.la

nettle_sha256_SOURCES       =
libnettle_sha256_la_SOURCES = nettle-sha256.c

nettle_sha256_LDADD         = $(DUMMY_CRT0) \
                              $(top_builddir)/support/libsupport.la \
                              libnettle-sha256.la \
                              $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)

endif
