# Makefile for BEEBS testsuite directory
#
# Copyright (C) 2018 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

#
# SPDX-License-Identifier: GPL-3.0-or-later

AUTOMAKE_OPTIONS = dejagnu

SUBDIRS = beebs.test config lib

EXTRA_DIST = beebs-conf.exp

# Testing flags

DEJATOOL = beebs
export DEJAGNU
export BENCHMARKS
AM_RUNTESTFLAGS = --target_board @BOARD@
