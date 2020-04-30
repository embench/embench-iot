#!/usr/bin/env python3

# Script to benchmark size

# Copyright (C) 2017, 2019 Embecosm Limited
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
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

from json import loads
from elftools.elf.elffile import ELFFile

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
    # List arguments are empty by default, a user specified value then takes
    # precedence. If the list is empty after parsing, then we can install a
    # default value.
    parser.add_argument(
        '--text',
        type=str,
        default=[],
        action='append',
        help='Section name(s) containing code'
    )
    parser.add_argument(
        '--data',
        type=str,
        default=[],
        action='append',
        help='Section name(s) containing non-zero initialized writable data'
    )
    parser.add_argument(
        '--rodata',
        type=str,
        default=[],
        action='append',
        help='Section name(s) containing read only data'
    )
    parser.add_argument(
        '--bss',
        type=str,
        default=[],
        action='append',
        help='Section name(s) containing zero initialized writable data'
    )
    parser.add_argument(
        '--metric',
        type=str,
        default=[],
        action='append',
        choices=['text', 'rodata', 'data', 'bss'],
        help='Sections to include in metric: one or more of "text", "rodata", '
        + '"data" or "bss". Default "text"',
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
    gp['json'] = args.json_output

    # Sort out the list of section names to use
    gp['secnames'] = dict()

    for argname in ['text', 'rodata', 'data', 'bss']:
        secnames = getattr(args, argname)
        if secnames:
            gp['secnames'][argname] = secnames
        else:
            gp['secnames'][argname] = ['.' + argname]

    # If no sections are specified, we just use .text
    if args.metric:
        gp['metric'] = args.metric
    else:
        gp['metric'] = ['text']

def get_section_group_by_name(elf, name):
    """ Get a group of sections matching with the provided name from the file.
        Return None if no such section exists.
    """
    # The first time this method is called, construct a name to number
    # mapping
    #
    if elf._section_name_map is None:
        elf._section_name_map = {}
        for i, sec in enumerate(elf.iter_sections()):
            elf._section_name_map[sec.name] = i

    sec_group = {}
    for i, sec in enumerate(elf.iter_sections()):
        if sec.name.startswith(name):
            secnum = elf._section_name_map.get(sec.name, None)
            sec_group[sec.name] = elf.get_section(secnum)

    return None if sec_group is None else sec_group

def benchmark_size(bench):
    """Compute the total size of the desired sections in a benchmark.  Returns
       the size in bytes, which may be zero if the section wasn't found."""
    appexe = os.path.join(gp['bd_benchdir'], bench, bench)
    sec_size = 0

    with open(appexe, 'rb') as fileh:
        elf = ELFFile(fileh)
        for metric in gp['metric']:
            for secname in gp['secnames'][metric]:
                sections = get_section_group_by_name(elf, secname)
                if sections:
                    for sec in sections:
                        sec_size += sections[sec]['sh_size']

    # Return the section (group) size
    return sec_size


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
    gp['baseline_dir'] = os.path.join(
        gp['rootdir'], 'baseline-data', 'size.json')
    with open(gp['baseline_dir']) as fileh:
        baseline_all = loads(fileh.read())

    # Compute the baseline data we need
    baseline = {}

    for bench, data in baseline_all.items():
        baseline[bench] = 0
        for sec in gp['metric']:
            baseline[bench] += data[sec]

    # Collect data and output it
    successful = True
    raw_data = {}
    rel_data = {}
    if gp['json']:
        log.info('  "size results" :')
        log.info('  { "detailed size results" :')
    else:
        log.info('Benchmark            size')
        log.info('---------            ----')

    for bench in benchmarks:
        raw_data[bench] = benchmark_size(bench)
        rel_data[bench] = {}
        output = {}

        # Zero is a valid section size, although empty .text should be a
        # concern.
        if gp['absolute']:
            # Want absolute results. Only include non-zero values
            if gp['json']:
                output = f'{raw_data[bench]}'
            else:
                output = f' {raw_data[bench]:8,}'
        else:
            # Want relative results (the default). If baseline is zero, just
            # use 0.0 as the value.  Note this is inverted compared to the
            # speed benchmark, so SMALL is good.
            if baseline[bench] > 0:
                rel_data[bench] = raw_data[bench] / baseline[bench]
            else:
                rel_data[bench] = 0.0
            if gp['json']:
                output = f'{rel_data[bench]:.2f}'
            else:
                output = f'   {rel_data[bench]:6.2f}'

        if gp['json']:
            if bench == benchmarks[0]:
                log.info('    { ' + f'"{bench}" : {output},')
            elif bench == benchmarks[-1]:
                log.info(f'      "{bench}" : {output}')
            else:
                log.info(f'      "{bench}" : {output},')
        else:
            log.info(f'{bench:15} {output:8}')

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
        opt_comma = ',' if args.json_comma else ''
        embench_stats(benchmarks, raw_data, rel_data, 'size', opt_comma)
        log.info('All benchmarks sized successfully')
    else:
        log.info('ERROR: Failed to compute size benchmarks')
        sys.exit(1)


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
