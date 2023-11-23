/* Copyright (C) 2017 Embecosm Limited and University of Bristol

   Contributor Graham Markall <graham.markall@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#define CPU_MHZ 10
// redefines main() to WASM_ENTRY
#define WASM 1
#define WASM_ENTRY _run()