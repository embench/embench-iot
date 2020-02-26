/* Dummy C runtime for the benchmarks

   Copyright (C) 2018-2019 Embecosm Limited

   Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

/* The purpose of this library is to measure the size of code excluding target
   dependent C library code.

   Some target linker scripts (e.g. RISC-V, ARM) use _start as the entry point -
   others (e.g. ARC) use __start.  */

extern int main (int argc, char *argv[]);


void
_start (void)
{
  (void) main (0, 0);
}

void
__start (void)
{
  (void) main (0, 0);
}

void
__init (void)
{
  (void) main (0, 0);
}

/*
   Local Variables:
   mode: C
   c-file-style: "gnu"
   End:
*/
