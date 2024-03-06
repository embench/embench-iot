/* Copyright (C) 2012 Embecosm Limited and University of Bristol

   Contributor: Daniel Torres <dtorres@hmc.edu>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <support.h>
#include <stdint.h>
#include <stdlib.h>

//defined in the assembly file, either crt0.S for speed or dummy.S for size
extern void start_trigger();
extern void stop_trigger();

void
initialise_board ()
{
}