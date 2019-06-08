# Main configure script for BEEBS

# Copyright (C) 2013-2014 Embecosm Limited and the University of Bristol
# Copyright (C) 2018 Embecosm Limited

# Contributor James Pallister <james.pallister@embecosm.com>
# Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>

# This file is part of Embench and was formerly part of the Bristol/Embecosm
# Embedded Benchmark Suite.

# SPDX-License-Identifier: GPL-3.0-or-later

# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.68])

# AC_PROG_CC and other commands will set CFLAGS to "-O2 -g", which in this
# case we don't want untless the user has explicitly requested, so we save and
# restore flags across this call.

OLD_CFLAGS=$CFLAGS

AC_INIT([beebs], [3.0], [beebs@mageec.org])
AC_CONFIG_MACRO_DIR([m4])

AC_CANONICAL_BUILD
AC_CANONICAL_HOST
AC_CANONICAL_TARGET

AM_INIT_AUTOMAKE([-Wno-portability])
AM_EXTRA_RECURSIVE_TARGETS([spell])
AM_MAINTAINER_MODE([disable])
AM_SILENT_RULES([yes])

# List of all benchmarks

bmlist="aha-mont64            \
        crc32                 \
        cubic                 \
        edn                   \
        huffbench             \
        matmult-int           \
        minver                \
        nbody                 \
        nettle-aes            \
        nettle-sha256         \
        nsichneu              \
        picojpeg              \
        qrduino               \
        sglib-combined        \
        slre                  \
        st                    \
        statemate             \
        ud                    \
        wikisort"

# Set default values enabling all architectures

benchmark_aha_mont64=true
benchmark_crc32=true
benchmark_cubic=true
benchmark_edn=true
benchmark_huffbench=true
benchmark_matmult_int=true
benchmark_minver=true
benchmark_nbody=true
benchmark_nettle_aes=true
benchmark_nettle_sha256=true
benchmark_nsichneu=true
benchmark_picojpeg=true
benchmark_qrduino=true
benchmark_sglib_combined=true
benchmark_slre=true
benchmark_st=true
benchmark_statemate=true
benchmark_ud=true
benchmark_wikisort=true

# Work out which architecture we are targeting
# Also pass this through to be substituted

arch=$host_cpu

# Option for selecting the target board

AC_ARG_WITH([board],
    [AS_HELP_STRING([--with-board], [Select the board to target])],
    [board=$with_board],
    [board=none])

# Option for selecting the target chip

AC_ARG_WITH([chip],
[AS_HELP_STRING([--with-chip], [Select the chip to target])],
    [chip=$with_chip],
    [chip=generic])

# Default settings for dummy libraries. These can be overridden by the
# chip configuration or configure flags. We default to having them all
# off because we expect the default setup to produce compiled code that
# can actually be executed - however, the dummy libraries are helpful
# for analysing code size without library code inclusion confounding
# things.

USE_DUMMY_CRT0=no
USE_DUMMY_LIBGCC=no
USE_DUMMY_COMPILERRT=no
USE_DUMMY_LIBC=no
USE_DUMMY_LIBM=no

# Execute any architecture, board or chip specific configuration. These can
# set architecture, chip and board CPPFLAGS, CFLAGS and LDFLAGS and exclude
# individual tests by setting benchmark_<bm> to false.

# We can't use AC_CHECK_FILE, because we are cross-compiling, and that
# prohibits use of AC_CHECK_FILE.

AS_IF([test -f $srcdir/config/$arch/arch.cfg],
      [source $srcdir/config/$arch/arch.cfg], [])

AS_IF([test -d $srcdir/config/$arch/chips/$chip],
      [], [AC_MSG_ERROR([Chip config directory "$chip" does not exist])])

AS_IF([test -f $srcdir/config/$arch/chips/$chip/chip.cfg],
      [source $srcdir/config/$arch/chips/$chip/chip.cfg], [])

AS_IF([test -d $srcdir/config/$arch/boards/$board],
      [], [AC_MSG_ERROR([Board config directory "$board" does not exist])])

AS_IF([test -f $srcdir/config/$arch/boards/$board/board.cfg ],
      [source $srcdir/config/$arch/boards/$board/board.cfg], [])

# Options for enabling/disabling each test in alphabetical order (see
# genmacros.sh for a script to generate all of this). To add one new test just
# insert the same pattern at the correct place in the list.

# Remember that ctl, matmult, sglib-arraysort and trio are not benchmarks
# themselves, but the frameworks from which others are created.

# NOTE. There is the m4_foreach macro, but getting it to work for this seems to
# be impossible

AC_ARG_ENABLE([benchmark-aha-mont64],
  [AS_HELP_STRING([--enable-benchmark-aha-mont64],
     [Enable benchmark aha-mont64])],
  [case "${enableval}" in
      yes) benchmark_aha_mont64=true ;;
      no)  benchmark_aha_mont64=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-aha-mont64]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_AHA_MONT64],
               [test x$benchmark_aha_mont64 = xtrue])

AC_ARG_ENABLE([benchmark-crc32],
  [AS_HELP_STRING([--enable-benchmark-crc32],
     [Enable benchmark crc32])],
  [case "${enableval}" in
      yes) benchmark_crc32=true ;;
      no)  benchmark_crc32=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-crc32]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_CRC32],
               [test x$benchmark_crc32 = xtrue])

AC_ARG_ENABLE([benchmark-cubic],
  [AS_HELP_STRING([--enable-benchmark-cubic],
     [Enable benchmark cubic])],
  [case "${enableval}" in
      yes) benchmark_cubic=true ;;
      no)  benchmark_cubic=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-cubic]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_CUBIC],
               [test x$benchmark_cubic = xtrue])

AC_ARG_ENABLE([benchmark-edn],
  [AS_HELP_STRING([--enable-benchmark-edn],
     [Enable benchmark edn])],
  [case "${enableval}" in
      yes) benchmark_edn=true ;;
      no)  benchmark_edn=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-edn]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_EDN],
               [test x$benchmark_edn = xtrue])

AC_ARG_ENABLE([benchmark-huffbench],
  [AS_HELP_STRING([--enable-benchmark-huffbench],
     [Enable benchmark huffbench])],
  [case "${enableval}" in
      yes) benchmark_huffbench=true ;;
      no)  benchmark_huffbench=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-huffbench]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_HUFFBENCH],
               [test x$benchmark_huffbench = xtrue])

AC_ARG_ENABLE([benchmark-matmult-int],
  [AS_HELP_STRING([--enable-benchmark-matmult-int],
     [Enable benchmark matmult-int])],
  [case "${enableval}" in
      yes) benchmark_matmult_int=true ;;
      no)  benchmark_matmult_int=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-matmult-int]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_MATMULT_INT],
               [test x$benchmark_matmult_int = xtrue])

AC_ARG_ENABLE([benchmark-minver],
  [AS_HELP_STRING([--enable-benchmark-minver],
     [Enable benchmark minver])],
  [case "${enableval}" in
      yes) benchmark_minver=true ;;
      no)  benchmark_minver=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-minver]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_MINVER],
               [test x$benchmark_minver = xtrue])

AC_ARG_ENABLE([benchmark-nbody],
  [AS_HELP_STRING([--enable-benchmark-nbody],
     [Enable benchmark nbody])],
  [case "${enableval}" in
      yes) benchmark_nbody=true ;;
      no)  benchmark_nbody=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-nbody]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_NBODY],
               [test x$benchmark_nbody = xtrue])

AC_ARG_ENABLE([benchmark-nettle-aes],
  [AS_HELP_STRING([--enable-benchmark-nettle-aes],
     [Enable benchmark nettle-aes])],
  [case "${enableval}" in
      yes) benchmark_nettle_aes=true ;;
      no)  benchmark_nettle_aes=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-nettle-aes]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_NETTLE_AES],
               [test x$benchmark_nettle_aes = xtrue])

AC_ARG_ENABLE([benchmark-nettle-sha256],
  [AS_HELP_STRING([--enable-benchmark-nettle-sha256],
     [Enable benchmark nettle-sha256])],
  [case "${enableval}" in
      yes) benchmark_nettle_sha256=true ;;
      no)  benchmark_nettle_sha256=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-nettle-sha256]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_NETTLE_SHA256],
               [test x$benchmark_nettle_sha256 = xtrue])

AC_ARG_ENABLE([benchmark-nsichneu],
  [AS_HELP_STRING([--enable-benchmark-nsichneu],
     [Enable benchmark nsichneu])],
  [case "${enableval}" in
      yes) benchmark_nsichneu=true ;;
      no)  benchmark_nsichneu=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-nsichneu]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_NSICHNEU],
               [test x$benchmark_nsichneu = xtrue])

AC_ARG_ENABLE([benchmark-picojpeg],
  [AS_HELP_STRING([--enable-benchmark-picojpeg],
     [Enable benchmark picojpeg])],
  [case "${enableval}" in
      yes) benchmark_picojpeg=true ;;
      no)  benchmark_picojpeg=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-picojpeg]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_PICOJPEG],
               [test x$benchmark_picojpeg = xtrue])

AC_ARG_ENABLE([benchmark-qrduino],
  [AS_HELP_STRING([--enable-benchmark-qrduino],
     [Enable benchmark qrduino])],
  [case "${enableval}" in
      yes) benchmark_qrduino=true ;;
      no)  benchmark_qrduino=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-qrduino]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_QRDUINO],
               [test x$benchmark_qrduino = xtrue])

AC_ARG_ENABLE([benchmark-sglib-combined],
  [AS_HELP_STRING([--enable-benchmark-sglib-combined],
     [Enable benchmark sglib-combined])],
  [case "${enableval}" in
      yes) benchmark_sglib_combined=true ;;
      no)  benchmark_sglib_combined=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-sglib-combined]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_SGLIB_COMBINED],
               [test x$benchmark_sglib_combined = xtrue])

AC_ARG_ENABLE([benchmark-slre],
  [AS_HELP_STRING([--enable-benchmark-slre],
     [Enable benchmark slre])],
  [case "${enableval}" in
      yes) benchmark_slre=true ;;
      no)  benchmark_slre=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-slre]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_SLRE],
               [test x$benchmark_slre = xtrue])

AC_ARG_ENABLE([benchmark-st],
  [AS_HELP_STRING([--enable-benchmark-st],
     [Enable benchmark st])],
  [case "${enableval}" in
      yes) benchmark_st=true ;;
      no)  benchmark_st=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-st]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_ST],
               [test x$benchmark_st = xtrue])

AC_ARG_ENABLE([benchmark-statemate],
  [AS_HELP_STRING([--enable-benchmark-statemate],
     [Enable benchmark statemate])],
  [case "${enableval}" in
      yes) benchmark_statemate=true ;;
      no)  benchmark_statemate=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-statemate]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_STATEMATE],
               [test x$benchmark_statemate = xtrue])

AC_ARG_ENABLE([benchmark-ud],
  [AS_HELP_STRING([--enable-benchmark-ud],
     [Enable benchmark ud])],
  [case "${enableval}" in
      yes) benchmark_ud=true ;;
      no)  benchmark_ud=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-ud]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_UD],
               [test x$benchmark_ud = xtrue])

AC_ARG_ENABLE([benchmark-wikisort],
  [AS_HELP_STRING([--enable-benchmark-wikisort],
     [Enable benchmark wikisort])],
  [case "${enableval}" in
      yes) benchmark_wikisort=true ;;
      no)  benchmark_wikisort=false ;;
      *)   AC_MSG_ERROR([bad value ${enableval} for --enable-benchmark-wikisort]) ;;
   esac],
  [])
AM_CONDITIONAL([ENABLED_BENCHMARK_WIKISORT],
               [test x$benchmark_wikisort = xtrue])


# What to set DUMMY_* to if the dummy libraries are enabled.

DUMMY_CRT0_YES="\$(top_builddir)/support/libdummycrt0.la"
DUMMY_LIBGCC_YES="\$(top_builddir)/support/libdummygcc.la"
DUMMY_COMPILERRT_YES="\$(top_builddir)/support/libdummycompilerrt.la"
DUMMY_LIBC_YES="-Wl,--start-group \$(top_builddir)/support/libdummyc.la"
DUMMY_LIBM_YES="\$(top_builddir)/support/libdummym.la"

# Enable dummy libraries

case "${USE_DUMMY_CRT0}" in
   yes) DUMMY_CRT0=${DUMMY_CRT0_YES} ;;
   no)  DUMMY_CRT0= ;;
   *)   DUMMY_CRT0=${USE_DUMMY_CRT0} ;;
esac

case "${USE_DUMMY_LIBGCC}" in
   yes) DUMMY_LIBGCC=${DUMMY_LIBGCC_YES} ;;
   no)  DUMMY_LIBGCC= ;;
   *)   DUMMY_LIBGCC=${USE_DUMMY_LIBGCC} ;;
esac

case "${USE_DUMMY_COMPILERRT}" in
   yes) DUMMY_COMPILERRT=${DUMMY_COMPILERRT_YES} ;;
   no)  DUMMY_COMPILERRT= ;;
   *)   DUMMY_COMPILERRT=${USE_DUMMY_COMPILERRT} ;;
esac

case "${USE_DUMMY_LIBC}" in
   yes) DUMMY_LIBC=${DUMMY_LIBC_YES} ;;
   no)  DUMMY_LIBC= ;;
   *)   DUMMY_LIBC=${USE_DUMMY_LIBC} ;;
esac

case "${USE_DUMMY_LIBM}" in
   yes) DUMMY_LIBM=${DUMMY_LIBM_YES} ;;
   no)  DUMMY_LIBM="-lm" ;;
   *)   DUMMY_LIBM=${USE_DUMMY_LIBM} ;;
esac

# Control warmup

AC_ARG_ENABLE([warmup],
  [AS_HELP_STRING([--enable-warmup],
     [Enable warmup])],
  [case "${enableval}" in
      yes) AC_DEFINE([WARMUP_HEAT],[3],[How much warmup is needed]) ;;
      no)  AC_DEFINE([WARMUP_HEAT],[0],[How much warmup is needed]) ;;
      *)   AC_DEFINE_UNQUOTED([WARMUP_HEAT],
      	[${enableval}],[How much warmup is needed]) ;;
   esac],
  [AC_DEFINE([WARMUP_HEAT],[1],[How much warmup is needed])])

# Check for support code

AM_CONDITIONAL([CHIPSUPPORT_C],
	       [test -f $srcdir/config/$arch/chips/$chip/chipsupport.c])

# Check for support headers

test -f $srcdir/config/$arch/boards/$board/boardsupport.h && \
    AC_DEFINE([HAVE_BOARDSUPPORT_H], [1], [Board support header is present])

test -f $srcdir/config/$arch/chips/$chip/chipsupport.h && \
    AC_DEFINE([HAVE_CHIPSUPPORT_H], [1], [Chip support header is present])

# Architecture, board and chip specific CPPFLAGS, CFLAGS and LDFLAGS. Convention is that one does not override CFLAGS, to allow
EMBENCH_CPPFLAGS="$ARCH_CPPFLAGS $CHIP_CPPFLAGS $BOARD_CPPFLAGS"
EMBENCH_CFLAGS="$ARCH_CFLAGS $CHIP_CFLAGS $BOARD_CFLAGS"
EMBENCH_LDFLAGS="$ARCH_LDFLAGS $CHIP_LDFLAGS $BOARD_LDFLAGS"

# There is a bug in LTO which breaks library building, so for now we turn off
# LTO for the dummy libraries
DUMMY_CPPFLAGS="$EMBENCH_CPPFLAGS"
DUMMY_CFLAGS="$EMBENCH_CFLAGS -fno-lto"
DUMMY_LDFLAGS="$EMBENCH_LDFLAGS -fno-lto"

LT_INIT
AC_SUBST([LIBTOOL_DEPS])

AC_PROG_CC()
AM_PROG_AS

# Set up testing

if test x"$DEJAGNU" = x
then
    DEJAGNU="\$(top_srcdir)/testsuite/beebs-conf.exp"
fi

# Restore the CFLAGS

CFLAGS=$OLD_CFLAGS

# Substitute flags

AC_SUBST([CPPFLAGS])
AC_SUBST([CFLAGS])
AC_SUBST([LDFLAGS])
AC_SUBST([EMBENCH_CPPFLAGS])
AC_SUBST([EMBENCH_CFLAGS])
AC_SUBST([EMBENCH_LDFLAGS])
AC_SUBST([DUMMY_CPPFLAGS])
AC_SUBST([DUMMY_CFLAGS])
AC_SUBST([DUMMY_LDFLAGS])

# Substitute dummy libraries

AC_SUBST([DUMMY_CRT0])
AC_SUBST([DUMMY_LIBGCC])
AC_SUBST([DUMMY_COMPILERRT])
AC_SUBST([DUMMY_LIBC])
AC_SUBST([DUMMY_LIBM])

# Substitute architecture, board and chip

AC_SUBST(ARCH, $arch)
AC_SUBST(BOARD, $board)
AC_SUBST(CHIP, $chip)

# Substitute DejaGnu variable

AC_SUBST([DEJAGNU])

# Substitute benchmark list

AC_SUBST([BENCHMARKS],$bmlist)

# Safety check we haven't been given a nonsense srcdir

AC_CONFIG_SRCDIR([src/])

# Generate the config.h

AC_CONFIG_HEADERS([config.h])

# Generate makefiles

AC_CONFIG_FILES([Makefile                          \
                 doc/Makefile                      \
                 src/Makefile                      \
		 src/aha-mont64/Makefile           \
                 src/crc32/Makefile                \
                 src/cubic/Makefile                \
                 src/edn/Makefile                  \
                 src/huffbench/Makefile            \
                 src/matmult-int/Makefile          \
                 src/minver/Makefile               \
                 src/nbody/Makefile                \
                 src/nettle-aes/Makefile           \
                 src/nettle-sha256/Makefile        \
                 src/nsichneu/Makefile             \
                 src/picojpeg/Makefile             \
                 src/qrduino/Makefile              \
                 src/sglib-combined/Makefile \
                 src/slre/Makefile                 \
                 src/st/Makefile                   \
                 src/statemate/Makefile            \
                 src/ud/Makefile                   \
                 src/wikisort/Makefile             \
		 support/Makefile                  \
		 testsuite/Makefile                \
		 testsuite/beebs.test/Makefile     \
		 testsuite/config/Makefile         \
		 testsuite/lib/Makefile])

# And spit it all out

AC_OUTPUT
