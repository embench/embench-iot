#!/usr/bin/env python3

# Script to benchmark size

# Copyright (C) 2017, 2019 Embecosm Limited
# Copyright (C) 2021 Roger Shepherd
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
# Contributor: Roger Shepherd <roger.shepherd@rcjd.net>
# Contributor: Konrad Moreon <konrad.moron@tum.de>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Compute the size benchmark for a set of compiled Embench programs.
"""

import argparse
import codecs
import os
import sys
import platform

from json import loads
from elftools.elf import elffile as elf
from elftools.elf.constants import SH_FLAGS as FLAGS

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

"""
This script only handles elf format files as they are the standard executable
format for microprocessors.

Categories of sections

This script is concerned with 3 categories of section. These sections are associated
by their elf flags. The default
associations are:

    category of section                    elf
    -----------------------------------   ------------
    executable code                       AX
    non-zero initialized writeable data   AW or AWX
    read onlydata                         A
"""

# the default sections names are used both in validate_args and in collect_data
DEFAULT_FLAGS_ELF =   { 'text'  : {int(FLAGS.SHF_ALLOC | FLAGS.SHF_EXECINSTR)},
                        'rodata': {int(FLAGS.SHF_ALLOC)},
                        'data'  : {int(FLAGS.SHF_ALLOC | FLAGS.SHF_WRITE), int(FLAGS.SHF_ALLOC | FLAGS.SHF_WRITE | FLAGS.SHF_EXECINSTR)},
                      }

DEFAULT_SECNAMELIST_DICT =  {'elf': DEFAULT_FLAGS_ELF,
                            }
"""
Metrics

The script reports a metric which is the sum of the sizes of a number of the
categories of sections. By default the metric reported is executable code (text)
category. This can be overridden using the `—metric` parameter which takes the space
separated list of categories to be included in the metric.
"""
# the categories and the metrics happen to be the same; they could be different
ALL_CATEGORIES = ['text', 'rodata', 'data']
ALL_METRICS    = ['text', 'rodata', 'data']


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
        '--dummy-benchmark', help='Dummy benchmark to measure library size overhead',
        default={}
    )
    # List arguments are empty by default, a user specified value then takes
    # precedence. If the list is empty after parsing, then we can install a
    # default value.
    parser.add_argument(
        '--metric',
        type=str,
        default=[],
        nargs='+',
        choices=ALL_METRICS,
        help='Section categories to include in metric: one or more of "text", "rodata", '
        + 'or "data". Default "text"',
    )
    parser.add_argument(
        '--file-extension',
        type=str,
        default=None,
        help='Optional file extension to append to bench mark names when searching for binaries.'
    )

    return parser


def validate_args(args):
    """Check that supplied args are all valid. By definition logging is
       working when we get here.

       Update the gp dictionary with all the useful info"""
    gp['format'] = 'elf'

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

    gp['bd_supportdir'] = os.path.join(gp['bd'], 'support')

    if os.path.isabs(args.baselinedir):
        gp['baseline_dir'] = args.baselinedir
    else:
        gp['baseline_dir'] = os.path.join(gp['rootdir'], args.baselinedir)

    gp['absolute'] = args.absolute
    if args.output_format:
        gp['output_format'] = args.output_format
    else:
        gp['output_format'] = output_format.TEXT

    # If no categories are specified, we just use text
    if args.metric:
        gp['metric'] = args.metric
    else:
        gp['metric'] = ['text']

    if args.dummy_benchmark:
        gp['dummy_benchmark'] = args.dummy_benchmark
    else:
        gp['dummy_benchmark'] = "dummy-benchmark"

    if args.file_extension is None:
        if platform.system() == 'Windows':
            gp['file_extension'] = '.exe'
        else:
            gp['file_extension'] = ''
    else:
        gp['file_extension'] = args.file_extension

def benchmark_size(bench, bd_path, metrics, dummy_sec_sizes):
    """Compute the total size of the desired sections in a benchmark.  Returns
       the size in bytes, which may be zero if the section wasn't found."""
    appexe = os.path.join(bd_path, bench, f"{bench}{gp['file_extension']}")
    sec_sizes = {}

    # If the benchmark failed to build, then return a 0 size instead of
    # crashing when failing to open the file.
    if not os.path.exists(appexe):
        return {}

    # read format from file and check it is as expected
    with open(appexe, 'rb') as fileh:
        magic = fileh.read(4)
        fileh.close()
    if ((magic != b'\x7fELF')):
        log.info(f'ERROR: Only ELF is supported, {appexe} does not contain magic identifier')
        sys.exit(1)

    #binary = lief.parse(appexe)
    
    binary = elf.ELFFile(open(appexe, 'rb'))
    sections = binary.iter_sections()
    for metric in metrics:
        sec_sizes[metric] = 0
        for section in sections:
            if (section['sh_flags'] in DEFAULT_FLAGS_ELF[metric]):
                sec_sizes[metric] += section['sh_size']
    for metric, size in dummy_sec_sizes.items():
        if metric in metrics:
            sec_sizes[metric] -= size
    # Return the section (group) size
    return sec_sizes


def collect_data(benchmarks):
    """Collect and log all the raw and optionally relative data associated with
       the list of benchmarks supplied in the "benchmarks" argument. Return
       the raw data and relative data as a list.  The raw data may be empty if
       there is a failure. The relative data will be empty if only absolute
       results have been requested.

       Note that we manually generate the JSON output, rather than using the
       dumps method, because the result will be manually edited, and we want
       to guarantee the layout."""

    # Baseline data is held external to the script. Import it here.
    size_baseline = os.path.join(gp['baseline_dir'], 'size.json')
    with open(size_baseline) as fileh:
        baseline_all = loads(fileh.read())

    # Compute the baseline data we need
    baseline = {}

    for bench, data in baseline_all.items():
        baseline[bench] = 0
        for sec in gp['metric']:
            baseline[bench] += data[sec]

    successful = True
    raw_section_data = {}
    raw_totals = {}
    rel_data = {}

    # Collect data
    if isinstance(gp['dummy_benchmark'], str):
        dummy_section_data = benchmark_size(gp['dummy_benchmark'], gp['bd_supportdir'], ALL_METRICS, {})
    else:
        dummy_section_data = {}
    if dummy_section_data == {}:
        dummy_benchmark_abs_path = os.path.join(gp['bd_supportdir'], gp['dummy_benchmark'])
        log.error(f'ERROR: could not find dummy benchmark at {dummy_benchmark_abs_path}')
        sys.exit(1)
    for bench in benchmarks:
        if gp['output_format'] == output_format.BASELINE:
            raw_section_data[bench] = benchmark_size(bench, gp['bd_benchdir'], ALL_METRICS, dummy_section_data)
        else:
            raw_section_data[bench] = benchmark_size(bench, gp['bd_benchdir'], gp['metric'], dummy_section_data)
        raw_totals[bench] = sum(raw_section_data[bench].values())

        # Calculate data relative to the baseline if needed
        if gp['absolute'] or gp['output_format'] == output_format.BASELINE:
            rel_data[bench] = {}
        else:
            # Want relative results (the default). If baseline is zero, just
            # use 0.0 as the value.  Note this is inverted compared to the
            # speed benchmark, so SMALL is good.
            if baseline[bench] > 0:
                rel_data[bench] = raw_totals[bench] / baseline[bench]
            else:
                rel_data[bench] = 0.0

    # Output it
    if gp['output_format'] == output_format.JSON:
        log.info('{  "size results" :')
        log.info('  { "detailed size results" :')
        for bench in benchmarks:
            res_output = ''
            if gp['absolute']:
                res_output = f'{raw_totals[bench]}'
            else:
                res_output = f'{rel_data[bench]:.2f}'

            if bench == benchmarks[0]:
                log.info('    { ' + f'"{bench}" : {res_output},')
            elif bench == benchmarks[-1]:
                log.info(f'      "{bench}" : {res_output}')
            else:
                log.info(f'      "{bench}" : {res_output},')

        log.info('    },')
    elif gp['output_format'] == output_format.TEXT:
        log.info('Benchmark            size')
        log.info('---------            ----')
        for bench in benchmarks:
            res_output = ''
            if gp['absolute']:
                res_output = f' {raw_totals[bench]:8,}'
            else:
                res_output = f'   {rel_data[bench]:6.2f}'
            log.info(f'{bench:15} {res_output:8}')
    elif gp['output_format'] == output_format.BASELINE:
        log.info('{')
        for bench in benchmarks:
            res_output = ''
            for metric in ALL_METRICS:
                # newline before the first metric
                if metric != ALL_METRICS[0]:
                    res_output += ',\n'
                value = raw_section_data[bench][metric]
                res_output += f'    "{metric}" : {value}'

            # comma after all but last benchmark in the log
            if bench == benchmarks[-1]:
                log.info(f'  "{bench}" : {{\n{res_output}\n  }}')
            else:
                log.info(f'  "{bench}" : {{\n{res_output}\n  }},')
        log.info('}')

    if successful:
        return raw_totals, rel_data

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
    setup_logging(args.logdir, 'size')
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
        if gp['output_format'] != output_format.BASELINE:
            opt_comma = ',' if args.json_comma else ''
            embench_stats(benchmarks, raw_data, rel_data)
            if gp['output_format'] == output_format.JSON: log.info('}')
            else: log.info('All benchmarks sized successfully')
    else:
        log.info('ERROR: Failed to compute size benchmarks')
        sys.exit(1)


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
