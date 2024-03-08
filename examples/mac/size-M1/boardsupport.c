/* Copyright (C) 2019 Clemson University

   Contributor Ola Jeppsson <ola.jeppsson@gmail.com>
   Contributor Roger Shepherd <rog!@rcjd.net>
   This file is part of Embench.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <stdio.h>
#include <time.h>
#include <support.h>

// for the moment:
// 		we measure real time and cpu time
// 		we use real time for reporting results
// 		experiments reporting both on Mac Mini M1 they differed insignificantly
static struct timespec begin_r, end_r; // real time
static struct timespec begin_c, end_c; // CPU time

void
initialise_board ()
{
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
start_trigger ()
{
    clock_gettime(CLOCK_REALTIME, &begin_r);
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &begin_c);
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
stop_trigger ()
{
	// clocks report in ns but quantum is 1 us
	// update rate differes between x86 and Apple Silicon Mac
    clock_gettime(CLOCK_REALTIME, &end_r);
    long seconds_r = end_r.tv_sec - begin_r.tv_sec;
    long nanoseconds_r = end_r.tv_nsec - begin_r.tv_nsec;
    double elapsed_r = seconds_r + nanoseconds_r*1e-9;

    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end_c);
    long seconds_c = end_c.tv_sec - begin_c.tv_sec;
    long nanoseconds_c = end_c.tv_nsec - begin_c.tv_nsec;
    double elapsed_c = seconds_c + nanoseconds_c*1e-9;

    // report time in ms
    printf("Real time: %.6f ms CPU time: %.6f ms \n", elapsed_r*1000.0, elapsed_c*1000.0);
}
