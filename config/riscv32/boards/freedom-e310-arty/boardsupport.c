/* Copyright (C) 2021 Hiroo HAYASHI

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <support.h>
#include <stdint.h>
#include <stdio.h>

// RTC is not implemented
// #include <metal/rtc.h>

// gdb "info reg mcycle" does not return proper value.
uint64_t mcycle;

void
clear_mcycle ()
{
  __asm__ volatile ("csrwi mcycle, 0");
  __asm__ volatile ("csrwi mcycleh, 0");
  __asm__ volatile ("csrwi mcycle, 0");
}

uint64_t
rdmcycle ()
{
  uint32_t lo, hi1, hi2;
  // cf. RISC-V Unprivileged ISA, 10.1 Base Counters and Timers
  __asm__ __volatile__ ("1:\n\t"                     \
                        "csrr %0, mcycleh\n\t"       \
                        "csrr %1, mcycle\n\t"        \
                        "csrr %2, mcycleh\n\t"       \
                        "bne  %0, %2, 1b\n\t"        \
                        : "=r" (hi1), "=r" (lo), "=r" (hi2));
  return (uint64_t)hi1 << 32 | lo;
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
initialise_board ()
{
  __asm__ volatile ("li a0, 0" : : : "memory");
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
start_trigger ()
{
  clear_mcycle();
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
stop_trigger ()
{
  mcycle = rdmcycle();
}
