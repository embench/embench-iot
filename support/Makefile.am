# Support library Makefile.am for building a BEEBS benchmark
#
# Copyright (C) 2018 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# SPDX-License-Identifier: GPL-3.0-or-later

AM_CPPFLAGS = @EMBENCH_CPPFLAGS@
AM_CFLAGS   = @EMBENCH_CFLAGS@
AM_LDFLAGS  = @EMBENCH_LDFLAGS@

noinst_LTLIBRARIES = libbeebsc.la    \
		     libdummycrt0.la \
                     libdummygcc.la  \
                     libdummyc.la    \
                     libdummym.la    \
		         libsupport.la

libbeebsc_la_SOURCES     = beebsc.c \
			   beebsc.h

libdummycrt0_la_SOURCES  = dummy-crt0.c
libdummygcc_la_SOURCES   = dummy-libgcc.c
libdummyc_la_SOURCES     = dummy-libc.c
libdummym_la_SOURCES     = dummy-libm.c

libdummycrt0_la_CPPFLAGS = @DUMMY_CPPFLAGS@
libdummygcc_la_CPPFLAGS  = @DUMMY_CPPFLAGS@
libdummyc_la_CPPFLAGS    = @DUMMY_CPPFLAGS@
libdummym_la_CPPFLAGS    = @DUMMY_CPPFLAGS@

libdummycrt0_la_CFLAGS   = @DUMMY_CFLAGS@
libdummygcc_la_CFLAGS    = @DUMMY_CFLAGS@
libdummyc_la_CFLAGS      = @DUMMY_CFLAGS@
libdummym_la_CFLAGS      = @DUMMY_CFLAGS@

libdummycrt0_la_LDFLAGS  = @DUMMY_LDFLAGS@
libdummygcc_la_LDFLAGS   = @DUMMY_LDFLAGS@
libdummyc_la_LDFLAGS     = @DUMMY_LDFLAGS@
libdummym_la_LDFLAGS     = @DUMMY_LDFLAGS@

libsupport_la_SOURCES    = main.c    \
                           board.c   \
                           support.h

if CHIPSUPPORT_C
libsupport_la_SOURCES   += chip.c
endif

libsupport_la_CPPFLAGS   = -I$(top_srcdir)/config/@ARCH@/boards/@BOARD@ \
                           -I$(top_srcdir)/config/@ARCH@/chips/@CHIP@
