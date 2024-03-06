/* Copyright (C) 2017 Embecosm Limited and University of Bristol

   Contributor Graham Markall <graham.markall@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <support.h>
#include <stdint.h>
#include "boardsupport.h"

/* DWT (Data Watchpoint and Trace) registers, only exists on ARM Cortex with a DWT unit */

#define DWT_CONTROL             (*((volatile uint32_t*)0xE0001000))
/*!< DWT Control register */

#define DWT_CYCCNTENA_BIT       (1UL<<0)
/*!< CYCCNTENA bit in DWT_CONTROL register */

#define DWT_CYCCNT              (*((volatile uint32_t*)0xE0001004))
/*!< DWT Cycle Counter register */

#define DEMCR                   (*((volatile uint32_t*)0xE000EDFC))
/*!< DEMCR: Debug Exception and Monitor Control Register */

#define TRCENA_BIT              (1UL<<24)
/*!< Trace enable bit in DEMCR register */

#define InitCycleCounter() \
  DEMCR |= TRCENA_BIT
  /*!< TRCENA: Enable trace and debug block DEMCR (Debug Exception and Monitor Control Register */

#define ResetCycleCounter() \
  DWT_CYCCNT = 0
  /*!< Reset cycle counter */

#define EnableCycleCounter() \
  DWT_CONTROL |= DWT_CYCCNTENA_BIT
  /*!< Enable cycle counter */

#define DisableCycleCounter() \
  DWT_CONTROL &= ~DWT_CYCCNTENA_BIT
  /*!< Disable cycle counter */

#define GetCycleCounter() \
  DWT_CYCCNT
  /*!< Read cycle counter register */


void
initialise_board ()
{
  InitCycleCounter();
  ResetCycleCounter();
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
start_trigger ()
{
  EnableCycleCounter();
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
stop_trigger ()
{
  ResetCycleCounter();
  DisableCycleCounter();
}
