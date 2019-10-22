/* BEEBS cubic benchmark

   This version, copyright (C) 2013-2019 Embecosm Limited and University of
   Bristol

   Contributor: James Pallister <james.pallister@bristol.ac.uk>
   Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later

   The original code is from http://www.snippets.org/. */

/* +++Date last modified: 05-Jul-1997 */

/*
 **  CUBIC.C - Solve a cubic polynomial
 **  public domain by Ross Cottrell
 */

#include <math.h>
#include "snipmath.h"

void
SolveCubic (double a, double b, double c, double d, int *solutions, double *x)
{
  double a1 = (b / a);
  double a2 = (c / a);
  double a3 = (d / a);
  double Q = (a1 * a1 - 3.0 * a2) / 9.0;
  double R = (2.0 * a1 * a1 * a1 - 9.0 * a1 * a2 + 27.0 * a3) / 54.0;
  double R2_Q3 = (R * R - Q * Q * Q);

  double theta;

  if (R2_Q3 <= 0)
    {
      *solutions = 3;
      theta = acos (R / sqrt (Q * Q * Q));
      x[0] = -2.0 * sqrt (Q) * cos (theta / 3.0) - a1 / 3.0;
      x[1] =
	-2.0 * sqrt (Q) * cos ((theta + 2.0 * PI) / 3.0) - a1 / 3.0;
      x[2] =
	-2.0 * sqrt (Q) * cos ((theta + 4.0 * PI) / 3.0) - a1 / 3.0;
    }
  else
    {
      *solutions = 1;
      x[0] = pow (sqrt (R2_Q3) + fabs (R), 1 / 3.0);
      x[0] += (Q) / x[0];
      x[0] *= (R < 0.0) ? 1 : -1;
      x[0] -= (a1 / 3.0);
    }
}

/* vim: set ts=3 sw=3 et: */


/*
   Local Variables:
   mode: C
   c-file-style: "gnu"
   End:
*/
