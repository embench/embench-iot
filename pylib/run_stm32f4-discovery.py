#!/usr/bin/env python3

# Python module to run programs on a stm32f4-discovery board

# Copyright (C) 2019 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Embench module to run benchmark programs.

This version is suitable for a gdbserver with simulator.
"""

__all__ = [
    'get_target_args',
    'build_benchmark_cmd',
    'decode_results',
]

import argparse
import re

from embench_core import log

cpu_mhz = 1

def get_target_args(remnant):
    """Parse left over arguments"""
    parser = argparse.ArgumentParser(description='Get target specific args')

    parser.add_argument(
        '--gdb-command',
        type=str,
        default='gdb',
        help='Command to invoke GDB',
    )
    parser.add_argument(
        '--gdbserver-command',
        type=str,
        default='gdbserver',
        help='Command to invoke the GDB server',
    )
    parser.add_argument(
        '--cpu-mhz',
        type=int,
        default=1,
        help='Processor clock speed in MHz'
    )

    return parser.parse_args(remnant)


def build_benchmark_cmd(bench, args):
    """Construct the command to run the benchmark.  "args" is a
       namespace with target specific arguments"""
    global cpu_mhz
    cpu_mhz = args.cpu_mhz

    cmd = [f'{args.gdb_command}']
    gdb_comms = [
        'set confirm off',
        'file {0}',
        'target extended-remote :4242',
        'load',
        'delete breakpoints',
        'break start_trigger',
        'break stop_trigger',
        'break _exit',
        'continue',
        'print /u *0xe0001004',
        'continue',
        'print /u *0xe0001004',
        'continue',
        'print /x $a0',
        'quit',
    ]

    for arg in gdb_comms:
        cmd.extend(['-ex', arg.format(bench)])

    return cmd


def decode_results(stdout_str, stderr_str):
    """Extract the results from the output string of the run. Return the
       elapsed time in milliseconds or zero if the run failed."""
    # Return code is in standard output. We look for the string that means we
    # hit a breakpoint on _exit, then for the string returning the value.
    rcstr = re.search(
        'Breakpoint 3 at.*exit\.c.*\$1 = (\d+)', stdout_str, re.S
    )
    if not rcstr:
        log.debug('Warning: Failed to find return code')
        return 0.0

    # The start and end cycle counts are in the stderr string
    starttime = re.search('\$1 = (\d+)', stdout_str, re.S)
    endtime = re.search('\$2 = (\d+)', stdout_str, re.S)
    if not starttime or not endtime:
        log.debug('Warning: Failed to find timing')
        return 0.0

    # Time from cycles to milliseconds
    global cpu_mhz
    return (int(endtime.group(1)) - int(starttime.group(1))) / cpu_mhz / 1000.0
