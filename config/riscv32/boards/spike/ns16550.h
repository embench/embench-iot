/* RISC-V rv32 tutorial examples

   Copyright (C) 2021 John Winans

   This file is part of Embench.

   SPDX-License-Identifier: GPL-3.0-or-later */


#ifndef ns16550_H
#define ns16550_H

#include <stdint.h>

// inferred from the qemu-system-riscv32 dtb values
#define NS16550_THR	(*((volatile uint8_t *)0x10000000))
#define NS16550_RBR	(*((volatile uint8_t *)0x10000000))
#define NS16550_IER	(*((volatile uint8_t *)0x10000001))
#define NS16550_IIR	(*((volatile uint8_t *)0x10000002))
#define NS16550_FCR	(*((volatile uint8_t *)0x10000002))
#define NS16550_LCR	(*((volatile uint8_t *)0x10000003))
#define NS16550_MCR	(*((volatile uint8_t *)0x10000004))
#define NS16550_LSR	(*((volatile uint8_t *)0x10000005))
#define NS16550_MSR	(*((volatile uint8_t *)0x10000006))
#define NS16550_SCR	(*((volatile uint8_t *)0x10000007))

#define NS16550_LSR_THRE	(1<<5)

/**
* Wait for the TX FIFO to have room for a byte and send it.
***************************************************************************/
inline __attribute__((always_inline)) void ns16550_tx(uint8_t ch)
{
	// be careful about order of operations here...
	while((NS16550_LSR & NS16550_LSR_THRE) == 0)
		;
	NS16550_THR = ch;
}

#endif

