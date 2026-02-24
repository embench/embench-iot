#!/usr/bin/env python3

# Python module to run programs on an openocd server

# Copyright (C) 2021 Hiroo HAYASHI
# Copyright (C) 2019 Embecosm Limited
#
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Embench module to run benchmark programs.

This version is suitable for an openocd server.
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
        default='riscv64-unknown-elf-gdb',
        help='Command to invoke GDB',
    )
    parser.add_argument(
        '--gdbserver-command',
        type=str,
        default='extended-remote',
        help='Command to invoke the GDB server',
    )
    parser.add_argument(
        '--gdbserver-target',
        type=str,
        default='localhost:3333',
        help='target argument to the GDB server',
    )

    return parser.parse_args(remnant)


def build_benchmark_cmd(bench, args):
    """Construct the command to run the benchmark.  "args" is a
       namespace with target specific arguments"""

    cmd = [f'{args.gdb_command}', '-q']
    gdb_comms = [
        'set confirm off',
        'set style enabled off',
        'set height 0',
        'file {0}',
        'set remotetimeout 240',
        f'target {args.gdbserver_command} {args.gdbserver_target}',
        'monitor reset halt',
        'monitor flash protect 0 64 last off',
        'load',
        'break _exit',
        'monitor echo \"running {0}\n\"',
        'run',
        'p exit_status',
        'p/x mcycle',
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
    rcstr = re.search('^\$1 = (\d+)', stdout_str, re.M)
    if not rcstr:
        log.debug('Warning: Failed to find return code')
        return 0.0
    exit_status = int(rcstr.group(1))
    if exit_status:
        log.debug('Warning: verify_benchmark() failed')
        return 0.0

    # mcycle
    rcstr = re.search('^\$2 = 0x(\w+)', stdout_str, re.M)
    if not rcstr:
        log.debug('Warning: Failed to find mcycle value')
        return 0.0
    mcycle = int(rcstr.group(1), 16)

    # mcycle @32.5MHz clock
    ms_elapsed = float(mcycle) / 32500.0
    return ms_elapsed
