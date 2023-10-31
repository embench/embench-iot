/* Copyright (C) lowRISC contributors

   This file is part of Embench.

   SPDX-License-Identifier: GPL-3.0-or-later OR Apache-2.0 */

#include <stdint.h>
#include <stddef.h>

void *memset(void *s, int c, size_t n);
void *memcpy(void *dest, const void *src, size_t n);
int strcmp(const char *s1, const char *s2);
unsigned int strlen(const char *s);

void print(const char *s);
void print_hex(size_t x);
void printn(const char *s, int len);

#define SYS_exit 93
#define SYS_read 63
#define SYS_write 64

uintptr_t syscall(uintptr_t n, uintptr_t a0, uintptr_t a1, uintptr_t a2,
                  uintptr_t a3, uintptr_t a4, uintptr_t a5, uintptr_t a6);

void shutdown(int code);

void tohost_exit(uintptr_t code);
