/* Common dummy benchmark

   Copyright (C) 2018-2024 Embecosm Limited

   Contributor: Konrad Moron <konrad.moron@tum.de>

   SPDX-License-Identifier: GPL-3.0-or-later */

/* This is just a wrapper for the board specific support file. */
#define MAGIC 0xBE
void __attribute__ ((noinline))
initialise_benchmark (void)
{
}



void __attribute__ ((noinline))
warm_caches (int  heat)
{
}


int __attribute__ ((noinline))
benchmark (void)
{
  return MAGIC;
}


int __attribute__ ((noinline))
verify_benchmark (int r)
{
  return r == MAGIC;
}
#undef MAGIC