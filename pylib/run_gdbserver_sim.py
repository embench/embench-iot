#!/usr/bin/env python3

# Python module to run programs on a gdbserver with simulator

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
        '--gdbserver-target',
        type=str,
        default='ri5cy',
        help='target argument to gdbserver',
    )

    return parser.parse_args(remnant)


def build_benchmark_cmd(bench, args):
    """Construct the command to run the benchmark.  "args" is a
       namespace with target specific arguments"""

    cmd = [f'{args.gdb_command}']
    gdb_comms = [
        'set confirm off',
        'set style enabled off',
        'set height 0',
        'file {0}',
        f'target remote | {args.gdbserver_command} '
        + f'-c {args.gdbserver_target} --stdin',
        'stepi',
        'stepi',
        'load',
        'break start_trigger',
        'break stop_trigger',
        'break _exit',
        'jump *_start',
        'monitor cyclecount',
        'continue',
        'monitor cyclecount',
        'continue',
        'print $a0',
        'detach',
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
        'Breakpoint 3,.*\$1 = (\d+)', stdout_str, re.S
    )
    if not rcstr:
        log.debug('Warning: Failed to find return code')
        return 0.0

    # The start and end cycle counts are in the stderr string
    times = re.search('(\d+)\D+(\d+)', stderr_str, re.S)
    if times:
        ms_elapsed = float(int(times.group(2)) - int(times.group(1))) / 1000.0
        return ms_elapsed

    # We must have failed to find a time
    log.debug('Warning: Failed to find timing')
    return 0.0
