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

if ENABLED_BENCHMARK_QRDUINO

include $(top_srcdir)/src/common.mk.am

bin_PROGRAMS          = qrduino
noinst_LTLIBRARIES    = libqrduino.la

qrduino_SOURCES       =
libqrduino_la_SOURCES = qrtest.c   \
                        qrencode.c \
                        qrencode.h \
                        qrframe.c  \
                        ecctable.h \
                        qrbits.h

qrduino_LDADD         = $(DUMMY_CRT0) \
                        $(top_builddir)/support/libsupport.la \
                        libqrduino.la \
                        $(top_builddir)/support/libbeebsc.la \
                      $(DUMMY_LIBC) $(DUMMY_LIBGCC) $(DUMMY_COMPILERRT)



endif
