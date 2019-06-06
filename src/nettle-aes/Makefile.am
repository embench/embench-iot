# Makefile.am for nettle-aes
#
# Copyright (C) 2019 Embecosm Limited and University of Bristol
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# Contributor: Graham Markall <graham.markall@embecosm.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if ENABLED_BENCHMARK_NETTLE_AES

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS             = nettle-aes
noinst_LTLIBRARIES       = libnettle-aes.la

nettle_aes_SOURCES       =
libnettle_aes_la_SOURCES = nettle-aes.c

nettle_aes_LDADD         = $(DUMMY_CRT0) \
                           $(top_builddir)/support/libsupport.la \
                           libnettle-aes.la \
                           $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)

endif
