#!/usr/bin/env python3

# Script to benchmark execution speed.

# Copyright (C) 2017, 2019 Embecosm Limited
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Benchmark speed.

This version is suitable when using a version of GDB which can launch a GDB
server to use as a target.
"""

import argparse
import os
import re
import subprocess
import sys

from json import loads

from embench_core import log
from embench_core import gp
from embench_core import setup_logging
from embench_core import log_args
from embench_core import find_benchmarks
from embench_core import log_benchmarks
from embench_core import embench_stats


def build_parser():
    """Build a parser for all the arguments"""
    parser = argparse.ArgumentParser(description='Compute the size benchmark')

    parser.add_argument(
        '--builddir',
        type=str,
        default='bd',
        help='Directory holding all the binaries',
    )
    parser.add_argument(
        '--logdir',
        type=str,
        default='logs',
        help='Directory in which to store logs',
    )
    parser.add_argument(
        '--absolute',
        action='store_true',
        help='Specify to show absolute results',
    )

    return parser


def validate_args(args):
    """Check that supplied args are all valid. By definition logging is
       working when we get here.

       Update the gp dictionary with all the useful info"""
    if os.path.isabs(args.builddir):
        gp['bd'] = args.builddir
    else:
        gp['bd'] = os.path.join(gp['rootdir'], args.builddir)

    if not os.path.isdir(gp['bd']):
        log.error(f'ERROR: build directory {gp["bd"]} not found: exiting')
        sys.exit(1)

    if not os.access(gp['bd'], os.R_OK):
        log.error(f'ERROR: Unable to read build directory {gp["bd"]}: exiting')
        sys.exit(1)

    gp['absolute'] = args.absolute


def build_benchmark_cmd(bench):
    """Construct the command to run the benchmark"""
    gdb_comms = [
        'set style enabled off',
        'set height 0',
        'file {0}',
        'target remote | riscv32-gdbserver -c ri5cy --stdin',
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
    cmd = ['riscv32-unknown-elf-gdb']

    for arg in gdb_comms:
        cmd.extend(['-ex', arg.format(bench)])

    return cmd


def decode_results(stdout_str, stderr_str):
    """Extract the results from the output string of the run. Return the
       elapsed time in milliseconds or zero if the run failed."""
    # Return code is in standard output. We look for the string that means we
    # hit a breakpoint on _exit, then for the string returning the value.
    rcstr = re.search(
        'Breakpoint 3, _exit.*at.*exit\.c.*\$1 = (\d+)', stdout_str, re.S
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


def benchmark_speed(bench):
    """Time the benchmark.  Result is a time in milliseconds, or zero on
       failure."""
    succeeded = True
    appdir = os.path.join(gp['bd_benchdir'], bench)
    appexe = os.path.join(appdir, bench)

    if os.path.isfile(appexe):
        arglist = build_benchmark_cmd(bench)
        try:
            res = subprocess.run(
                arglist,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=appdir,
                timeout=30,
            )
            if res.returncode != 0:
                log.warning(f'Warning: Run of {bench} failed.')
                succeeded = False
        except subprocess.TimeoutExpired:
            log.warning(f'Warning: Run of {bench} timed out.')
            succeeded = False
    else:
        log.warning(f'Warning: {bench} executable not found.')
        succeeded = False

    # Process results
    if succeeded:
        exec_time = decode_results(
            res.stdout.decode('utf-8'), res.stderr.decode('utf-8')
        )
        succeeded = exec_time > 0

    if succeeded:
        return exec_time
    else:
        log.debug('Args to subprocess:')
        log.debug(f'{arglist}')
        if 'res' in locals():
            log.debug(res.stdout.decode('utf-8'))
            log.debug(res.stderr.decode('utf-8'))
        return 0.0


def collect_data(benchmarks):
    """Collect and log all the raw and optionally relative data associated with
       the list of benchmarks supplied in the "benchmarks" argument. Return
       the raw data and relative data as a list.  The raw data may be empty if
       there is a failure. The relative data will be empty if only absolute
       results have been requested."""

    # Baseline data is held external to the script. Import it here.
    gp['baseline_dir'] = os.path.join(gp['rootdir'], 'baseline-speed.json')
    with open(gp['baseline_dir']) as fileh:
        baseline = loads(fileh.read())

    # Collect data and output it
    successful = True
    raw_data = {}
    rel_data = {}
    log.info('Benchmark           Speed')
    log.info('---------            ----')

    for bench in benchmarks:
        raw_data[bench] = benchmark_speed(bench)
        rel_data[bench] = 0.0
        if raw_data[bench] == 0.0:
            del raw_data[bench]
            del rel_data[bench]
            successful = False
        else:
            output = ''
            if gp['absolute']:
                # Want absolute results. Only include non-zero values
                output = f'{round(raw_data[bench]):8,}'
            else:
                # Want relative results (the default). Only use non-zero values.
                rel_data[bench] = raw_data[bench] / baseline[bench]
                output = f'  {rel_data[bench]:6.2f,}'

            log.info(f'{bench:15}  {output:8}')

    if successful:
        return raw_data, rel_data

    # Otherwise failure return
    return [], []


def main():
    """Main program driving measurement of benchmark size"""
    # Establish the root directory of the repository, since we know this file is
    # in that directory.
    gp['rootdir'] = os.path.abspath(os.path.dirname(__file__))

    # Parse arguments using standard technology
    parser = build_parser()
    args = parser.parse_args()

    # Establish logging
    setup_logging(args.logdir, 'speed')
    log_args(args)

    # Check args are OK (have to have logging and build directory set up first)
    validate_args(args)

    # Find the benchmarks
    benchmarks = find_benchmarks()
    log_benchmarks(benchmarks)

    # Collect the size data for the benchmarks
    raw_data, rel_data = collect_data(benchmarks)

    # We can't compute geometric SD on the fly, so we need to collect all the
    # data and then process it in two passes. We could do the first processing
    # as we collect the data, but it is clearer to do the three things
    # separately. Given the size of datasets with which we are concerned the
    # compute overhead is not significant.
    if raw_data:
        embench_stats(benchmarks, raw_data, rel_data)
        log.info('All benchmarks run successfully')
    else:
        log.info('ERROR: Failed to compute speed benchmarks')
        sys.exit(1)


# Only run if this is the main package

if __name__ == '__main__':
    sys.exit(main())
