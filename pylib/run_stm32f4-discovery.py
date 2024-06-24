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

import argparse
import subprocess
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

    return parser.parse_args(remnant)


def build_benchmark_cmd(path, args):
    """Construct the command to run the benchmark.  "args" is a
       namespace with target specific arguments"""
    cmd = [f'{args.gdb_command}']
    gdb_comms = [
        'set confirm off',
        'file {0}',
        'target extended-remote :3333',
        'load',
        'delete breakpoints',
        'break start_trigger',
        'break stop_trigger',
        'break AtExit',
        'continue',
        'print /u *0xe0001004',
        'continue',
        'print /u *0xe0001004',
        'continue',
        'print /u $r0',
        'quit',
    ]

    for arg in gdb_comms:
        cmd.extend(['-ex', arg.format(path)])

    return cmd


def decode_results(stdout_str, args):
    """Extract the results from the output string of the run. Return the
       elapsed time in milliseconds or zero if the run failed."""
    # Return code is in standard output. We look for the string that means we
    # hit a breakpoint on _exit, then for the string returning the value.
    rcstr = re.search(
        'Breakpoint 3,.*\$3 = (\d+)', stdout_str, re.S
    )
    if not rcstr:
        log.debug('Warning: Failed to find return code')
        return 0.0
    if int(rcstr.group(1)) != 0:
        log.debug('Warning: Error return code')

    # The start and end cycle counts are in the stdout string
    starttime = re.search('\$1 = (\d+)', stdout_str, re.S)
    endtime = re.search('\$2 = (\d+)', stdout_str, re.S)
    if not starttime or not endtime:
        log.debug('Warning: Failed to find timing')
        return 0.0

    # Time from cycles to milliseconds
    cycles = int(endtime.group(1)) - int(starttime.group(1))
    return cycles / args.cpu_mhz / 1000.0

def run_benchmark(bench, path, args):
    """Runs the benchmark "bench" at "path". "args" is a namespace
       with target specific arguments. This function will be called
       in parallel unless if the number of tasks is limited via
       command line. "run_benchmark" should return the result in
       milliseconds.
    """
    arglist = build_benchmark_cmd(path, args)
    try:
        res = subprocess.run(
            arglist,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=50,
        )
    except subprocess.TimeoutExpired:
        log.warning(f'Warning: Run of {bench} timed out.')
        return None
    if res.returncode != 0:
        print ('Non-zero return code')
        return None
    return decode_results(res.stdout.decode('utf-8'), args)
