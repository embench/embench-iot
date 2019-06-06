/* Common board.c for the benchmarks

   Copyright (C) 2018-2019 Embecosm Limited

   Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

/* This is just a wrapper for the chip specific support file if there is one. */

#include "config.h"

#ifdef HAVE_CHIPSUPPORT_H
#include "chipsupport.c"
#endif

/* Standard C does not permit empty translation units, so provide one. */

static void
empty_func ()
{
}

/*
   Local Variables:
   mode: C
   c-file-style: "gnu"
   End:
*/
