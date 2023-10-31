/* Copyright (C) lowRISC contributors

   This file is part of Embench.

   SPDX-License-Identifier: GPL-3.0-or-later OR Apache-2.0 */

#include "util.h"

volatile uint64_t tohost __attribute__((section(".htif")));
volatile uint64_t fromhost __attribute__((section(".htif")));
#define TOHOST   (*(volatile uint64_t*)0x0002000)
#define FROMHOST (*(volatile uint64_t*)0x0002008)

uintptr_t syscall(uintptr_t n, uintptr_t a0, uintptr_t a1, uintptr_t a2,
                  uintptr_t a3, uintptr_t a4, uintptr_t a5, uintptr_t a6)
{
    uint64_t th = tohost;
    if(th) {
        __builtin_trap();
        while(1) {}
    }

    static volatile uint64_t htif_mem[8];
    htif_mem[0] = n;
    htif_mem[1] = a0;
    htif_mem[2] = a1;
    htif_mem[3] = a2;
    htif_mem[4] = a3;
    htif_mem[5] = a4;
    htif_mem[6] = a5;
    htif_mem[7] = a6;
    tohost = (uintptr_t)htif_mem;

    while(1) {
        uint64_t fh = fromhost;
        if(fh) {
            fromhost = 0;
            break;
        }
    }

    return htif_mem[0];
}

void shutdown(int code) {
    syscall(SYS_exit, code, 0, 0, 0, 0, 0, 0);
    while(1) {}
}

void print(const char *s) {
    syscall(SYS_write, 0, (uintptr_t)s, (uintptr_t)strlen(s), 0, 0, 0, 0);
}

void printn(const char *s, int len) {
    syscall(SYS_write, 0, (uintptr_t)s, (uintptr_t)len, 0, 0, 0, 0);
}

void __attribute__((noreturn)) tohost_exit(uintptr_t code)
{
  tohost = (code << 1) | 1;
  while (1);
}
