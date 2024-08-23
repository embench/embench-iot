/* Copyright (C) 2017 Embecosm Limited and University of Bristol

   Contributor Graham Markall <graham.markall@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <stdint.h>
#include <support.h>

volatile uint32_t start_cycles_hi;
volatile uint32_t start_cycles_lo;
volatile uint32_t stop_cycles_hi;
volatile uint32_t stop_cycles_lo;

void
initialise_board ()
{
  __asm__ volatile ("li a0, 0" : : : "memory");
}

void __attribute__ ((noinline))
start_trigger ()
{

  // Enable cycle counting by clearing the CY bit of mcountinhibit, then read
  // the cycles into start_time
  __asm__ volatile("csrci mcountinhibit, 0x1"); // mcountinhibit.cy = 0
  __asm__ volatile("rdcycle %0" : "=r"(start_cycles_lo));
  __asm__ volatile("rdcycleh %0" : "=r"(start_cycles_hi));
}

void __attribute__ ((noinline))
stop_trigger ()
{
  __asm__ volatile("rdcycle %0" : "=r"(stop_cycles_lo));
  __asm__ volatile("rdcycleh %0" : "=r"(stop_cycles_hi));
}
