
#include <support.h>
#include <stdio.h>
#include <or1k-support.h>
#include <or1k-sprs.h>
#include <inttypes.h>
#include <stdint.h>

#define BOARD_CPU_HZ 1000000UL

uint32_t _or1k_board_uart_base = 0x90000000;
uint32_t _or1k_board_uart_baud = 9600;
uint32_t _or1k_board_clk_freq = BOARD_CPU_HZ;

static volatile uint32_t start = 0;
static volatile uint32_t end = 0;

void
initialise_board ()
{
   or1k_timer_init (BOARD_CPU_HZ);
   /* TTMR[M]=0b11, continuous mode. */
   or1k_timer_set_mode (3u);
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
start_trigger ()
{
   or1k_timer_enable ();
   start = or1k_mfspr (OR1K_SPR_TICK_TTCR_ADDR);
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
stop_trigger ()
{
   uint32_t elapsed;

   end = or1k_mfspr (OR1K_SPR_TICK_TTCR_ADDR);
   elapsed = end - start;
   printf ("End time %" PRIu32 "\n", elapsed);
}
