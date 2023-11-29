/* BEEBS nbody benchmark

   This version, copyright (C) 2014-2019 Embecosm Limited and University of
   Bristol

   Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later

   The original source code for this benchmark can be found here:

     http://benchmarksgame.alioth.debian.org/

   and was released under the following licence, disclaimers, and
   copyright:

   Revised BSD license

   This is a specific instance of the Open Source Initiative (OSI) BSD
   license template http://www.opensource.org/licenses/bsd-license.php

   Copyright 2004-2009 Brent Fulgham
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions
   are met:

   Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

   Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.

   Neither the name of "The Computer Language Benchmarks Game" nor the
   name of "The Computer Language Shootout Benchmarks" nor the names
   of its contributors may be used to endorse or promote products
   derived from this software without specific prior written
   permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
   FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
   COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
   INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
   STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
   OF THE POSSIBILITY OF SUCH DAMAGE.  */

#include <math.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

#include "support.h"

#define LOCAL_SCALE_FACTOR 1

#define PI 3.141592653589793
#define SOLAR_MASS ( 4 * PI * PI )
#define DAYS_PER_YEAR 365.24

struct body
{
  double x[3], fill, v[3], mass;
};

#define BODIES_SIZE 5
static const struct body solar_bodies_init[BODIES_SIZE] = {
  /* sun */
  {
   .x = {0., 0., 0.},
   .v = {0., 0., 0.},
   .mass = SOLAR_MASS},
  /* jupiter */
  {
   .x = {4.84143144246472090e+00,
	 -1.16032004402742839e+00,
	 -1.03622044471123109e-01},
   .v = {1.66007664274403694e-03 * DAYS_PER_YEAR,
	 7.69901118419740425e-03 * DAYS_PER_YEAR,
	 -6.90460016972063023e-05 * DAYS_PER_YEAR},
   .mass = 9.54791938424326609e-04 * SOLAR_MASS},
  /* saturn */
  {
   .x = {8.34336671824457987e+00,
	 4.12479856412430479e+00,
	 -4.03523417114321381e-01},
   .v = {-2.76742510726862411e-03 * DAYS_PER_YEAR,
	 4.99852801234917238e-03 * DAYS_PER_YEAR,
	 2.30417297573763929e-05 * DAYS_PER_YEAR},
   .mass = 2.85885980666130812e-04 * SOLAR_MASS},
  /* uranus */
  {
   .x = {1.28943695621391310e+01,
	 -1.51111514016986312e+01,
	 -2.23307578892655734e-01},
   .v = {2.96460137564761618e-03 * DAYS_PER_YEAR,
	 2.37847173959480950e-03 * DAYS_PER_YEAR,
	 -2.96589568540237556e-05 * DAYS_PER_YEAR},
   .mass = 4.36624404335156298e-05 * SOLAR_MASS},
  /* neptune */
  {
   .x = {1.53796971148509165e+01,
	 -2.59193146099879641e+01,
	 1.79258772950371181e-01},
   .v = {2.68067772490389322e-03 * DAYS_PER_YEAR,
	 1.62824170038242295e-03 * DAYS_PER_YEAR,
	 -9.51592254519715870e-05 * DAYS_PER_YEAR},
   .mass = 5.15138902046611451e-05 * SOLAR_MASS}
};
static struct body solar_bodies[BODIES_SIZE];

void
offset_momentum (struct body *bodies, unsigned int nbodies)
{
  unsigned int i, k;
  for (i = 0; i < nbodies; ++i)
    for (k = 0; k < 3; ++k)
      bodies[0].v[k] -= bodies[i].v[k] * bodies[i].mass / SOLAR_MASS;
}


double
bodies_energy (struct body *bodies, unsigned int nbodies)
{
  double dx[3], distance, e = 0.0;
  unsigned int i, j, k;

  for (i = 0; i < nbodies; ++i)
    {
      e += bodies[i].mass * (bodies[i].v[0] * bodies[i].v[0]
			     + bodies[i].v[1] * bodies[i].v[1]
			     + bodies[i].v[2] * bodies[i].v[2]) / 2.;

      for (j = i + 1; j < nbodies; ++j)
	{
	  for (k = 0; k < 3; ++k)
	    dx[k] = bodies[i].x[k] - bodies[j].x[k];

	  distance = sqrt (dx[0] * dx[0] + dx[1] * dx[1] + dx[2] * dx[2]);
	  e -= (bodies[i].mass * bodies[j].mass) / distance;
	}
    }
  return e;
}

void
initialise_benchmark (void)
{
  assert(sizeof (solar_bodies_init) / sizeof (solar_bodies_init[0]) == BODIES_SIZE);
}



static int benchmark_body (int  rpt);

void
warm_caches (int  heat)
{
  assert(memcpy(solar_bodies, solar_bodies_init, sizeof(solar_bodies)));
  int  res = benchmark_body (heat);
  assert(memcpy(solar_bodies, solar_bodies_init, sizeof(solar_bodies)));

  return;
}


int
benchmark (void)
{
  return benchmark_body (LOCAL_SCALE_FACTOR * CPU_MHZ);
}

void expand_universe(void)
{
  for (int i = 0; i < BODIES_SIZE; i++) {
    solar_bodies[i].x[0] *= 1.01;
    solar_bodies[i].x[1] *= 1.01;
    solar_bodies[i].x[2] *= 1.01;
    solar_bodies[i].v[0] *= 1.01;
    solar_bodies[i].v[1] *= 1.01;
    solar_bodies[i].v[2] *= 1.01;
    // Evaporation or something
    solar_bodies[i].mass /= 1.01;
  }
}

static int __attribute__ ((noinline))
benchmark_body (int rpt)
{
  int j;
  double tot_e = 0.0;

  for (j = 0; j < rpt; j++)
    {
      int i;
      offset_momentum (solar_bodies, BODIES_SIZE);
      /*printf("%.9f\n", bodies_energy(solar_bodies, BODIES_SIZE)); */
      for (i = 0; i < 100; ++i) {
        expand_universe();
	tot_e += bodies_energy (solar_bodies, BODIES_SIZE);
      }
      /*printf("%.9f\n", bodies_energy(solar_bodies, BODIES_SIZE)); */
    }
  /* Result is known good value for total energy. */
  // printf("%.20f\n", tot_e);
  return double_eq_beebs(tot_e, 20.58416113689254700603);
}


int
verify_benchmark (int tot_e_ok)
{
  int i, j;
  /* print expected values */
  // printf("static struct body solar_bodies[] = {\n");
  // for (i=0; i<BODIES_SIZE; i++) {
  //    printf("  {\n");
  //    printf("    .x = { %.30g, %.30g, %.30g },\n", solar_bodies[i].x[0],  solar_bodies[i].x[1],  solar_bodies[i].x[2]);
  //    printf("    .v = { %.30g, %.30g, %.30g },\n", solar_bodies[i].v[0],  solar_bodies[i].v[1],  solar_bodies[i].v[2]);
  //    printf("    .mass = %.30g\n", solar_bodies[i].mass);
  //    printf("  }");
  //    if (i<BODIES_SIZE-1) printf(",");
  //    printf("\n");
  // }
  // printf("};\n");
  static struct body expected[] = {
    {
      .x = { 0, 0, 0 },
      .v = { -0.00104855734495182826085390992432, -0.00885923642007596483238796025717, 6.47417045569482606931499546477e-05 },
      .mass = 14.5956136333422072937082702992
    },
    {
      .x = { 13.095170719774786860511994746, -3.13844970164038450377574918093, -0.280278338918426239700920632458 },
      .v = { 1.64000001291839869743682811531, 7.60590090628090553792617356521, -0.0682109733730176942545497809078 },
      .mass = 0.0139357742334713305409898964626
    },
    {
      .x = { 22.5672536834432406749328947626, 11.1568121998214788703762678779, -1.09145571910624816780455148546 },
      .v = { -2.73395642996889920439684829034, 4.93807682955851579009731722181, 0.0227630677564963739001324682931 },
      .mass = 0.00417268131699198401018957582664
    },
    {
      .x = { 34.8768691133459114439574477728, -40.8728512897969551431742729619, -0.604005427603493738608619878505 },
      .v = { 2.92874808859631841073678515386, 2.3497069853436709507832347299, -0.0293002674523172371157109239448 },
      .mass = 0.000637280110856412534102444222839
    },
    {
      .x = { 41.5992174485631238667338038795, -70.1069206062228715836681658402, 0.484861608121297582574271700651 },
      .v = { 2.6482581528317457042476235074, 1.60855007588536924600930433371, -0.0940083891021896989048656223531 },
      .mass = 0.000751876838177645951365180021497
    }
  };

  /* Check we have the correct total energy and we have set up the
     solar_bodies array correctly. */

  if (tot_e_ok)
    for (i = 0; i < BODIES_SIZE; i++)
      {
	for (j = 0; j < 3; j++)
	  {
	    if (double_neq_beebs(solar_bodies[i].x[j], expected[i].x[j]))
	      return 0;
	    if (double_neq_beebs(solar_bodies[i].v[j], expected[i].v[j]))
	      return 0;
	  }
	if (double_neq_beebs(solar_bodies[i].mass, expected[i].mass))
	  return 0;
      }
  else
    return 0;

  return 1;
}


/*
   Local Variables:
   mode: C
   c-file-style: "gnu"
   End:
*/
