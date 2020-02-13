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
import importlib
import os
import subprocess
import sys

from json import loads

sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pylib')
)

from embench_core import check_python_version
from embench_core import log
from embench_core import gp
from embench_core import setup_logging
from embench_core import log_args
from embench_core import find_benchmarks
from embench_core import log_benchmarks
from embench_core import embench_stats


def get_common_args():
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
    parser.add_argument(
        '--relative',
        dest='absolute',
        action='store_false',
        help='Specify to show relative results (the default)',
    )
    parser.add_argument(
        '--json-output',
        action='store_true',
        help='Specify to output in JSON format',
    )
    parser.add_argument(
        '--text-output',
        dest='json_output',
        action='store_false',
        help='Specify to output as plain text (the default)',
    )
    parser.add_argument(
        '--json-comma',
        action='store_true',
        help='Specify to append a comma to the JSON output',
    )
    parser.add_argument(
        '--no-json-comma',
        dest='json_comma',
        action='store_false',
        help='Specify to not append a comma to the JSON output',
    )
    parser.add_argument(
        '--target-module',
        type=str,
        required=True,
        help='Python module with routines to run benchmarks',
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout used for running each benchmark program'
    )

    return parser.parse_known_args()


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
    gp['timeout'] = args.timeout
    gp['json'] = args.json_output

    try:
        newmodule = importlib.import_module(args.target_module)
    except ImportError as error:
        log.error(
            f'ERROR: Target module import failure: {error}: exiting'
        )
        sys.exit(1)

    globals()['get_target_args'] = newmodule.get_target_args
    globals()['build_benchmark_cmd'] = newmodule.build_benchmark_cmd
    globals()['decode_results'] = newmodule.decode_results


def benchmark_speed(bench, target_args):
    """Time the benchmark.  "target_args" is a namespace of arguments
       specific to the target.  Result is a time in milliseconds, or zero on
       failure."""
    succeeded = True
    appdir = os.path.join(gp['bd_benchdir'], bench)
    appexe = os.path.join(appdir, bench)

    if os.path.isfile(appexe):
        arglist = build_benchmark_cmd(bench, target_args)
        try:
            res = subprocess.run(
                arglist,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=appdir,
                timeout=gp['timeout'],
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
        for arg in arglist:
            if arg == arglist[0]:
                comm = arg
            elif arg == '-ex':
                comm = ' ' + arg
            else:
                comm = " '" + arg + "'"

        log.debug('Args to subprocess:')
        log.debug(f'{comm}')
        if 'res' in locals():
            log.debug(res.stdout.decode('utf-8'))
            log.debug(res.stderr.decode('utf-8'))
        return 0.0


def collect_data(benchmarks, remnant):
    """Collect and log all the raw and optionally relative data associated with
       the list of benchmarks supplied in the "benchmarks" argument. "remant"
       is left over args from the command line, which may be useful to the
       benchmark running procs.

       Return the raw data and relative data as a list.  The raw data may be
       empty if there is a failure. The relative data will be empty if only
       absolute results have been requested."""

    # Baseline data is held external to the script. Import it here.
    gp['baseline_dir'] = os.path.join(
        gp['rootdir'], 'baseline-data', 'speed.json'
    )
    with open(gp['baseline_dir']) as fileh:
        baseline = loads(fileh.read())

    # Parse target specific args
    target_args = get_target_args(remnant)

    # Collect data and output it
    successful = True
    raw_data = {}
    rel_data = {}
    if gp['json']:
        log.info('  "speed results" :')
        log.info('  { "detailed speed results" :')
    else:
        log.info('Benchmark           Speed')
        log.info('---------           -----')

    for bench in benchmarks:
        raw_data[bench] = benchmark_speed(bench, target_args)
        rel_data[bench] = 0.0
        if raw_data[bench] == 0.0:
            del raw_data[bench]
            del rel_data[bench]
            successful = False
        else:
            output = ''
            if gp['absolute']:
                # Want absolute results. Only include non-zero values
                if gp['json']:
                    output = f'{round(raw_data[bench])}'
                else:
                    output = f'{round(raw_data[bench]):8,}'
            else:
                # Want relative results (the default). Only use non-zero
                # values.  Note this is inverted compared to the size
                # benchmark, so LARGE is good.
                rel_data[bench] = baseline[bench] / raw_data[bench]
                if gp['json']:
                    output = f'{rel_data[bench]:.2f}'
                else:
                    output = f'  {rel_data[bench]:6.2f}'

            if gp['json']:
                if bench == benchmarks[0]:
                    log.info('    { ' + f'"{bench}" : {output},')
                elif bench == benchmarks[-1]:
                    log.info(f'      "{bench}" : {output}')
                else:
                    log.info(f'      "{bench}" : {output},')
            else:
                # Want relative results (the default). Only use non-zero values.
                log.info(f'{bench:15}  {output:8}')

    if gp['json']:
        log.info('    },')

    if successful:
        return raw_data, rel_data

    # Otherwise failure return
    return [], []


def main():
    """Main program driving measurement of benchmark size"""
    # Establish the root directory of the repository, since we know this file is
    # in that directory.
    gp['rootdir'] = os.path.abspath(os.path.dirname(__file__))

    # Parse arguments common to all speed testers, and get list of those
    # remaining.
    args, remnant = get_common_args()

    # Establish logging
    setup_logging(args.logdir, 'speed')
    log_args(args)

    # Check args are OK (have to have logging and build directory set up first)
    validate_args(args)

    # Find the benchmarks
    benchmarks = find_benchmarks()
    log_benchmarks(benchmarks)

    # Collect the size data for the benchmarks. Pass any remaining args.
    raw_data, rel_data = collect_data(benchmarks, remnant)

    # We can't compute geometric SD on the fly, so we need to collect all the
    # data and then process it in two passes. We could do the first processing
    # as we collect the data, but it is clearer to do the three things
    # separately. Given the size of datasets with which we are concerned the
    # compute overhead is not significant.
    if raw_data:
        opt_comma = ',' if args.json_comma else ''
        embench_stats(benchmarks, raw_data, rel_data, 'speed', opt_comma)
        log.info('All benchmarks run successfully')
    else:
        log.info('ERROR: Failed to compute speed benchmarks')
        sys.exit(1)


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
