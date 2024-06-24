#!/usr/bin/env python3

# Script to benchmark execution speed.

# Copyright (C) 2017, 2019 Embecosm Limited
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
# Contributor: Konrad Moreon <konrad.moron@tum.de>
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
import sys
import platform

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
from embench_core import output_format


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
        '--baselinedir',
        type=str,
        default='baseline-data',
        help='Directory which contains baseline data',
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
        dest='output_format',
        action='store_const',
        const=output_format.JSON,
        help='Specify to output in JSON format',
    )
    parser.add_argument(
        '--text-output',
        dest='output_format',
        action='store_const',
        const=output_format.TEXT,
        help='Specify to output as plain text (the default)',
    )
    parser.add_argument(
        '--md-output',
        dest='output_format',
        action='store_const',
        const=output_format.MD,
        help='Specify to output as Markdown',
    )
    parser.add_argument(
        '--csv-output',
        dest='output_format',
        action='store_const',
        const=output_format.CSV,
        help='Specify to output as CSV',
    )
    parser.add_argument(
        '--baseline-output',
        dest='output_format',
        action='store_const',
        const=output_format.BASELINE,
        help='Specify to output in a format suitable for use as a baseline'
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
    parser.add_argument(
        '--file-extension',
        type=str,
        default=None,
        help='Optional file extension to append to bench mark names when searching for binaries.'
    )
    parser.add_argument(
        '--gsf',
        type=int,
        default=1,
        help='Global scale factor for benchmarks'
    )
    parser.add_argument(
        '--cpu-mhz',
        type=int,
        default=16,
        help='Processor clock speed in MHz'
    )

    return parser.parse_known_args()


def validate_args(args):
    """Check that supplied args are all valid. By definition logging is
       working when we get here.

       Update the gp dictionary with all the useful info"""
    gp['bd'] = args.builddir if os.path.isabs(args.builddir) else os.path.join(gp['rootdir'], args.builddir)

    if not os.path.isdir(gp['bd']):
        log.error(f'ERROR: build directory {gp["bd"]} not found: exiting')
        sys.exit(1)

    if not os.access(gp['bd'], os.R_OK):
        log.error(f'ERROR: Unable to read build directory {gp["bd"]}: exiting')
        sys.exit(1)

    gp['baseline_dir'] = args.baselinedir if os.path.isabs(args.baselinedir) else os.path.join(gp['rootdir'], args.baselinedir)

    gp['absolute'] = args.absolute
    if args.output_format:
        gp['output_format'] = args.output_format
    else:
        gp['output_format'] = output_format.TEXT

    gp['timeout'] = args.timeout

    if args.file_extension is None:
        gp['file_extension'] = '.exe' if platform.system() == 'Windows' else ''
    else:
        gp['file_extension'] = args.file_extension

    try:
        newmodule = importlib.import_module(args.target_module)
    except ImportError as error:
        log.error(
            f'ERROR: Target module import failure: {error}: exiting'
        )
        sys.exit(1)

    globals()['get_target_args'] = newmodule.get_target_args
    globals()['run_benchmark'] = newmodule.run_benchmark


def benchmark_speed(bench, args):
    """Time the benchmark.  "args" is a namespace of arguments, including
       those specific to the target.  Result is a time in milliseconds, or
       zero on failure."""
    appdir = os.path.join(gp['bd_benchdir'], bench)
    appexe = os.path.join(appdir,f"{bench}{gp['file_extension']}")

    if os.path.isfile(appexe):
        res = run_benchmark(bench, appexe, args)
        if res is None:
            log.warning(f'Warning: Run of {bench} failed.')
    else:
        log.warning(f'Warning: {bench} executable not found.')

    if res is None:
        print ('failed')
        return 0
    return res

def run_benchmarks(benchmarks, args):
    """Run the benchmarks, recording the raw times.

       return a flag indicating success, a list of the benchmarks run
       successfully  and the raw data as a dictionary.  Only benchmarks for
       which we suceeded will have an entry."""
    successful = True
    benchmarks_run = []
    raw_data = {}

    # Run the benchmarks
    for bench in benchmarks:
        raw_data[bench] = float(benchmark_speed(bench, args))

    # Delete the benchmark if it didn't succeed, record it if it did.
    for bench in benchmarks:
        if raw_data[bench] == 0.0:
            del raw_data[bench]
            successful = False
        else:
            benchmarks_run.append(bench)
            raw_data[bench] = float(raw_data[bench])

    return successful, benchmarks_run, raw_data

def compute_rel(benchmarks_run, raw_data, args):
    """Generate relative speed data.  Return a dictionary of relative
       scores.  In this case, we need to scale the raw scores by the scaling
       factor"""
    rel_data = {}

    # Get the baseline data
    speed_baseline = os.path.join(gp['baseline_dir'], 'speed.json')
    with open(speed_baseline) as fileh:
        baseline = loads(fileh.read())

    # We know there must be data
    for bench in benchmarks_run:
        rel_data[bench] = baseline[bench] / raw_data[bench] * args.gsf

    return rel_data

def output_json(benchmarks_run, raw_data, rel_data, args):
    """Output the data table in a JSON format.  We are given a list of
       benchmarks for which we have data"""
    log.info('{  "speed results" :')
    log.info('  { "detailed speed results" :')

    for bench in benchmarks_run:
        output = f'{round(raw_data[bench])}' if args.absolute else f'{rel_data[bench]:.2f}'

        if bench == benchmarks_run[0]:
            log.info(f'    {{ "{bench}" : {output},')
        elif bench == benchmarks_run[-1]:
            log.info(f'      "{bench}" : {output}')
        else:
            log.info(f'      "{bench}" : {output},')
    log.info('    },')

def output_text (benchmarks_run, raw_data, rel_data, args):
    """Output the data table in plain text format.  We are given a list of
       benchmarks for which we have data"""
    if gp['absolute']:
        log.info('Benchmark           Speed')
        log.info('---------           -----')
    else:
        log.info('Benchmark           Speed Speed/MHz')
        log.info('---------           ----- ---------')

    for bench in benchmarks_run:
        if gp['absolute']:
            output = f'{round(raw_data[bench]):8,}'
            log.info(f'{bench:15}  {output:8}')
        else:
            rel_per_mhz = rel_data[bench] / args.cpu_mhz
            output1 = f'  {rel_data[bench]:6.2f}'
            output2 = f'  {rel_per_mhz:6.2f}'
            log.info(f'{bench:15}  {output1:8}  {output2:8}')

def output_md (benchmarks_run, raw_data, rel_data, args):
    """Output the data table in Markdown format.  We are given a list of
       benchmarks for which we have data"""
    if gp['absolute']:
        log.info('| Benchmark       |      Speed |')
        log.info('| :-------------- | ---------: |')
    else:
        log.info('| Benchmark       |      Speed |  Speed/MHz |')
        log.info('| :-------------- | ---------: | ---------: |')

    for bench in benchmarks_run:
        if gp['absolute']:
            output = f'{round(raw_data[bench]):8,}'
            log.info(f'| {bench:15} |   {output:8} |')
        else:
            rel_per_mhz = rel_data[bench] / args.cpu_mhz
            output1 = f'  {rel_data[bench]:6.2f}'
            output2 = f'  {rel_per_mhz:6.2f}'
            log.info(f'| {bench:15} |   {output1:8} |   {output2:8} |')

def output_csv (benchmarks_run, raw_data, rel_data, args):
    """Output the data table in CSV format.  We are given a list of
       benchmarks for which we have data"""
    if gp['absolute']:
        log.info('"Benchmark","Speed"')
    else:
        log.info('"Benchmark","Speed","Speed/MHz"')

    for bench in benchmarks_run:
        if gp['absolute']:
            log.info(f'"{bench}","{round(raw_data[bench])}"')
        else:
            rel_per_mhz = rel_data[bench] / args.cpu_mhz
            log.info(f'"{bench}","{rel_data[bench]:.2f}","{rel_per_mhz:.2f}"')

def output_baseline(benchmarks_run, raw_data):
    """Output the data table in a JSON format for use as the baseline table.
       We are given a list of  benchmarks for which we have data"""
    log.info('{')
    for bench in benchmarks_run:
        if bench == benchmarks_run[-1]:
            log.info(f'  "{bench}" : {round(raw_data[bench]):0}')
        else:
            log.info(f'  "{bench}" : {round(raw_data[bench]):0},')

    log.info('}')

def collect_data(benchmarks, args):
    """Collect and log all the raw and optionally relative data associated with
       the list of benchmarks supplied in the "benchmarks" argument. "remant"
       is left over args from the command line, which may be useful to the
       benchmark running procs.

       Return the raw data and relative data as a list.  The raw data may be
       empty if there is a failure. The relative data will be empty if only
       absolute results have been requested."""

    # Get the raw data
    successful, benchmarks_run, raw_data = run_benchmarks(benchmarks, args)

    # Baseline data is held external to the script. Import it here if we are
    # doing relative output and then generate the relative data
    if not gp['absolute']:
        rel_data = compute_rel(benchmarks, raw_data, args)
    else:
        rel_data = {}

    # Output it
    if gp['output_format'] == output_format.JSON:
        output_json (benchmarks_run, raw_data, rel_data, args)
    elif gp['output_format'] == output_format.TEXT:
        output_text (benchmarks_run, raw_data, rel_data, args)
    elif gp['output_format'] == output_format.MD:
        output_md (benchmarks_run, raw_data, rel_data, args)
    elif gp['output_format'] == output_format.CSV:
        output_csv (benchmarks_run, raw_data, rel_data, args)
    elif gp['output_format'] == output_format.BASELINE:
        output_baseline(benchmarks_run, raw_data)

    if successful:
        return raw_data, rel_data

    # Otherwise failure return
    return [], []


def output_stats_json(geomean, geosd, georange, args):
    """Output the statistical summary in JSON format.

       Note that we manually generate the JSON output, rather than using the
       dumps method, because the result will be manually edited, and we want
       to guarantee the layout."""

    opt_comma = ',' if args.json_comma else ''
    if gp['absolute']:
        geomean_op = f'{int(geomean):0,}'
        geosd_op = f'{geosd:.2f}'
        georange_op = f'{int(georange):0,}'
    else:
        geomean_op = f'{geomean:.2f}'
        geosd_op = f'{geosd:.2f}'
        georange_op = f'{georange:.2f}'

    # Output the results
    log.info(f'    "speed geometric mean" : {geomean_op},')
    log.info(f'    "speed geometric standard deviation" : {geosd_op}')
    log.info(f'    "speed geometric range" : {georange_op}')
    log.info('  }' + f'{opt_comma}')


def output_stats_text(geomean, geosd, georange, args):
    """Output the statistical summary in plain text format."""

    if gp['absolute']:
        geomean_op = f'{int(geomean):8,}'
        geosd_op = f'     {geosd:6.2f}'
        georange_op = f'{int(georange):8,}'
    else:
        geomean_mhz = geomean / float(args.cpu_mhz)
        georange_mhz = georange / float(args.cpu_mhz)
        geomean_op = f'  {geomean:6.2f}'
        geosd_op = f'  {geosd:6.2f}'
        georange_op = f'  {georange:6.2f}'
        geomean_mhz_op = f'  {geomean_mhz:6.2f}'
        geosd_mhz_op = f'  {geosd:6.2f}'
        georange_mhz_op = f'  {georange_mhz:6.2f}'

    # Output the results
    if gp['absolute']:
        log.info('---------           -----')
        log.info(f'Geometric mean   {geomean_op}')
        log.info(f'Geometric SD     {geosd_op}')
        log.info(f'Geometric range  {georange_op}')
    else:
        log.info('---------           ----- ---------')
        log.info(f'Geometric mean   {geomean_op}  {geomean_mhz_op}')
        log.info(f'Geometric SD     {geosd_op}  {geosd_mhz_op}')
        log.info(f'Geometric range  {georange_op}  {georange_mhz_op}')

    log.info('All benchmarks run successfully')

def output_stats_md(geomean, geosd, georange, args):
    """Output the statistical summary in Markdown format."""

    if gp['absolute']:
        geomean_op = f'{int(geomean):8,}'
        geosd_op = f'  {geosd:6.2f}'
        georange_op = f'{int(georange):8,}'
    else:
        geomean_mhz = geomean / float(args.cpu_mhz)
        georange_mhz = georange / float(args.cpu_mhz)
        geomean_op = f'  {geomean:6.2f}'
        geosd_op = f'  {geosd:6.2f}'
        georange_op = f'  {georange:6.2f}'
        geomean_mhz_op = f'  {geomean_mhz:6.2f}'
        geosd_mhz_op = f'  {geosd:6.2f}'
        georange_mhz_op = f'  {georange_mhz:6.2f}'

        # Output the results
    if gp['absolute']:
        log.info('|                 |            |')
        log.info(f'| Geometric mean  |   {geomean_op} |')
        log.info(f'| Geometric SD    |   {geosd_op} |')
        log.info(f'| Geometric range |   {georange_op} |')
    else:
        log.info('|                 |            |            |')
        log.info(f'| Geometric mean  |   {geomean_op} |   {geomean_mhz_op} |')
        log.info(f'| Geometric SD    |   {geosd_op} |   {geosd_mhz_op} |')
        log.info(f'| Geometric range |   {georange_op} |   {georange_mhz_op} |')

def output_stats_csv(geomean, geosd, georange, args):
    """Output the statistical summary in CSV format."""

    if gp['absolute']:
        geomean_op = f'{int(geomean)}'
        geosd_op = f'{geosd:.2f}'
        georange_op = f'{int(georange)}'
    else:
        geomean_mhz = geomean / float(args.cpu_mhz)
        georange_mhz = georange / float(args.cpu_mhz)
        geomean_op = f'{geomean:.2f}'
        geosd_op = f'{geosd:.2f}'
        georange_op = f'{georange:.2f}'
        geomean_mhz_op = f'{geomean_mhz:.2f}'
        geosd_mhz_op = f'{geosd:.2f}'
        georange_mhz_op = f'{georange_mhz:.2f}'

    # Output the results
    if gp['absolute']:
        log.info(f'"Geometric mean","{geomean_op}"')
        log.info(f'"Geometric SD","{geosd_op}"')
        log.info(f'"Geometric range","{georange_op}"')
    else:
        log.info(f'"Geometric mean","{geomean_op}","{geomean_mhz_op}"')
        log.info(f'"Geometric SD","{geosd_op}","{geosd_mhz_op}"')
        log.info(f'"Geometric range","{georange_op}","{georange_mhz_op}"')

def generate_stats(benchmarks, raw_data, rel_data, args):
    """Generate the summary statistics at the end.  This is only computed when
       we have a successful run, so we know all benchmarks are represented."""
    if gp['output_format'] != output_format.BASELINE:
        geomean, geosd, georange = embench_stats(benchmarks, raw_data, rel_data)

    if gp['output_format'] == output_format.JSON:
        output_stats_json (geomean, geosd, georange, args)
    elif gp['output_format'] == output_format.TEXT:
        output_stats_text (geomean, geosd, georange, args)
    elif gp['output_format'] == output_format.MD:
        output_stats_md (geomean, geosd, georange, args)
    elif gp['output_format'] == output_format.CSV:
        output_stats_csv (geomean, geosd, georange, args)

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

    # Parse target specific args
    args = argparse.Namespace(**vars(args), **vars(get_target_args(remnant)))

    # Find the benchmarks
    benchmarks = find_benchmarks()
    log_benchmarks(benchmarks)

    # Collect the speed data for the benchmarks.
    raw_data, rel_data = collect_data(benchmarks, args)

    # We can't compute geometric SD on the fly, so we need to collect all the
    # data and then process it in two passes. We could do the first processing
    # as we collect the data, but it is clearer to do the three things
    # separately. Given the size of datasets with which we are concerned the
    # compute overhead is not significant.
    if raw_data:
        generate_stats(benchmarks, raw_data, rel_data, args)
    else:
        log.info('ERROR: Failed to compute speed benchmarks')
        sys.exit(1)


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
