/* Dummy standard C math library for the benchmarks

   Copyright (C) 2018-2019 Embecosm Limited

   Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

/* The purpose of this library is to measure the size of code excluding target
   dependent C library code. It only makes sense if it is used with
   -gc-sections. */

double
acos (double x __attribute__ ((unused)))
{
  return 0.0;
}


double
atan (double x __attribute__ ((unused)))
{
  return 0.0;
}


double
cos (double x __attribute__ ((unused)))
{
  return 0.0;
}


double
sin (double x __attribute__ ((unused)))
{
  return 0.0;
}


double
pow (double x __attribute__ ((unused)), double y __attribute__ ((unused)))
{
  return 0.0;
}


double
sqrt (double x __attribute__ ((unused)))
{
  return 0.0;
}


float
sqrtf (float x __attribute__ ((unused)))
{
  return 0.0;
}


double
floor (double x __attribute__ ((unused)))
{
  return 0.0;
}


float
floorf (float x __attribute__ ((unused)))
{
  return 0.0;
}


double
exp (double x __attribute__ ((unused)))
{
  return 0.0;
}

double
log (double x __attribute__ ((unused)))
{
  return 0.0;
}

/*
   Local Variables:
   mode: C
   c-file-style: "gnu"
   End:
*/
