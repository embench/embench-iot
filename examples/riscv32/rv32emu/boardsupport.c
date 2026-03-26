/* SPDX-License-Identifier: GPL-3.0-or-later */

#include <support.h>

void
initialise_board(void)
{
}

void __attribute__((noinline)) __attribute__((externally_visible))
start_trigger(void)
{
#if defined(__riscv)
    __asm__ volatile("li a0, 0" : : : "memory");
#endif
}

void __attribute__((noinline)) __attribute__((externally_visible))
stop_trigger(void)
{
#if defined(__riscv)
    __asm__ volatile("li a0, 0" : : : "memory");
#endif
}
