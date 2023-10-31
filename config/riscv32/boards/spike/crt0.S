/* Startup code for spike RISC-V ISA simulator with FPU enabled

   Copyright (C) 2017  SiFive Inc. All rights reserved.

   This file is part of Embench.

   SPDX-License-Identifier: GPL-3.0-or-later OR BSD-2-Clause */

; #include "newlib.h"

#define MSTATUS_FS          0x00006000
#define MSTATUS_XS          0x00018000

#=========================================================================
# crt0.S : Entry point for RISC-V user programs
#=========================================================================

  .text
  .global _start
  .type   _start, @function
  .section .text.startup
_start:
  # Initialize global pointer
.option push
.option norelax
1:auipc gp, %pcrel_hi(__global_pointer$)
  addi  gp, gp, %pcrel_lo(1b)
.option pop

  # enable FPU and accelerator if present
  li t0, MSTATUS_FS | MSTATUS_XS
  csrs mstatus, t0

  # Clear the bss segment
  la      sp, __ram_end__ 
  la      a0, __bss_start__
  la      a2, _end
  sub     a2, a2, a0
  li      a1, 0
  call    memset
#ifdef HAS_ATEXIT
#ifdef _LITE_EXIT
  # Make reference to atexit weak to avoid unconditionally pulling in
  # support code.  Refer to comments in __atexit.c for more details.
  .weak   atexit
  la      a0, atexit
  beqz    a0, .Lweak_atexit
  .weak   __libc_fini_array
#endif

  la      a0, __libc_fini_array   # Register global termination functions
  call    atexit                  #  to be called upon exit
#ifdef _LITE_EXIT
.Lweak_atexit:
#endif
#endif
  call    __libc_init_array       # Run global initialization functions

  #lw      a0, 0(sp)                  # a0 = argc
  #addi    a1, sp, __SIZEOF_POINTER__ # a1 = argv
  #li      a2, 0                      # a2 = envp = NULL
  li a0, 0
  li a1, 0
  li a2, 0
  call    main
  tail    exit
  .size  _start, .-_start
