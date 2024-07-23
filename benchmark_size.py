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
"""Compute the size benchmark for a set of compiled Embench programs.

This script only handles elf format files as they are the standard executable
format for microprocessors.

Categories of sections

This script is concerned with 4 categories of section. These sections are
associated by their ELF flags and ELF type. The default associations are:

    category of section                   Flags      Type
    -------------------                   -----      ----
    executable code                       AX         PROGBITS
    non-zero initialized writable data    AW or AWX  PROGBITS
    read only data                        A          PROGBITS
    zero initialized writable data (BSS)  AW or AWX  NOBITS

"""

import argparse
import os
import sys
import platform

from json import loads
from elftools.elf import elffile as elf
from elftools.elf.constants import SH_FLAGS as FLAGS

sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pylib'))

from embench_core import check_python_version
from embench_core import log
from embench_core import gp
from embench_core import setup_logging
from embench_core import log_args
from embench_core import find_benchmarks
from embench_core import log_benchmarks
from embench_core import embench_stats
from embench_core import output_format

# the default section flags and types are used both in validate_args and in
# collect_data.
DEFAULT_FLAGS_ELF = {
    'text': ({int(FLAGS.SHF_ALLOC | FLAGS.SHF_EXECINSTR)}, 'SHT_PROGBITS'),
    'rodata': ({int(FLAGS.SHF_ALLOC)}, 'SHT_PROGBITS'),
    'data': ({
        int(FLAGS.SHF_ALLOC | FLAGS.SHF_WRITE),
        int(FLAGS.SHF_ALLOC | FLAGS.SHF_WRITE | FLAGS.SHF_EXECINSTR)
    }, 'SHT_PROGBITS'),
    'bss': ({
        int(FLAGS.SHF_ALLOC | FLAGS.SHF_WRITE),
        int(FLAGS.SHF_ALLOC | FLAGS.SHF_WRITE | FLAGS.SHF_EXECINSTR)
    }, 'SHT_NOBITS'),
}

DEFAULT_SECNAMELIST_DICT = {
    'elf': DEFAULT_FLAGS_ELF,
}
"""
Metrics

The script reports a metric which is the sum of the sizes of a number of the
categories of sections. By default the metric reported is executable code (text)
category. This can be overridden using the `—metric` parameter which takes the space
separated list of categories to be included in the metric.
"""
# the categories and the metrics happen to be the same; they could be different
ALL_CATEGORIES = ['text', 'rodata', 'data', 'bss']
ALL_METRICS = ['text', 'rodata', 'data', 'bss']


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
        '--md-output',
        dest='output_format',
        action='store_const',
        const=output_format.MD,
        help='Specify to output as MarkDown',
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
        help='Specify to output in a format suitable for use as a baseline')
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
        '--dummy-benchmark',
        help='Dummy benchmark to measure library size overhead',
        default={})
    # List arguments are empty by default, a user specified value then takes
    # precedence. If the list is empty after parsing, then we can install a
    # default value.
    parser.add_argument(
        '--metric',
        type=str,
        default=[],
        nargs='+',
        choices=ALL_METRICS,
        help=
        'Section categories to include in metric: one or more of "text", "rodata", '
        + 'or "data". Default "text"',
    )
    parser.add_argument(
        '--file-extension',
        type=str,
        default=None,
        help=
        'Optional file extension to append to bench mark names when searching for binaries.'
    )

    return parser


def validate_build_dir(args):
    """Check that we have a valid build directory and update the gp dictionary
    accordingly."""
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


def validate_baseline_dir(args):
    """Set up the appropriate baseline directory."""
    if os.path.isabs(args.baselinedir):
        gp['baseline_dir'] = args.baselinedir
    else:
        gp['baseline_dir'] = os.path.join(gp['rootdir'], args.baselinedir)


def validate_output_format(args):
    """Set up the output format."""
    if args.output_format:
        gp['output_format'] = args.output_format
    else:
        gp['output_format'] = output_format.TEXT


def validate_metric(args):
    """Set up the metric(s) to be used.  If no categories are specified, we
    just use text."""
    if args.metric:
        gp['metric'] = args.metric
    else:
        gp['metric'] = ['text']


def validate_dummy_bm(args):
    """Set up the dummy benchmark to use, with a default if none specified."""
    if args.dummy_benchmark:
        gp['dummy_benchmark'] = args.dummy_benchmark
    else:
        gp['dummy_benchmark'] = "dummy-benchmark"


def validate_file_ext(args):
    """Set up the extension to be used with executables, using a default if
    none is specified."""
    if args.file_extension is None:
        if platform.system() == 'Windows':
            gp['file_extension'] = '.exe'
        else:
            gp['file_extension'] = ''
    else:
        gp['file_extension'] = args.file_extension


def validate_args(args):
    """Check that supplied args are all valid. By definition logging is
       working when we get here.

       Update the gp dictionary with all the useful info"""
    gp['format'] = 'elf'
    validate_build_dir(args)
    gp['bd_supportdir'] = os.path.join(gp['bd'], 'support')
    validate_baseline_dir(args)
    gp['absolute'] = args.absolute
    validate_output_format(args)
    validate_metric(args)
    validate_dummy_bm(args)
    validate_file_ext(args)


def check_for_elf(appexe):
    """Checked we have an ELF executable."""
    with open(appexe, 'rb') as fileh:
        magic = fileh.read(4)
        fileh.close()
    if magic != b'\x7fELF':
        log.info(
            f'ERROR: Only ELF is supported, {appexe} does not contain magic identifier'
        )
        sys.exit(1)


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
    check_for_elf(appexe)

    # TODO: We should insert the lief based anaysis here for use on Apple kit.
    #binary = lief.parse(appexe)

    with open(appexe, 'rb') as fileh:
        binary = elf.ELFFile(fileh)
        for metric in metrics:
            sec_sizes[metric] = 0
            sections = binary.iter_sections()
            for section in sections:
                metric_sh_flags_list = DEFAULT_FLAGS_ELF[metric][0]
                metric_sh_type = DEFAULT_FLAGS_ELF[metric][1]
                for metric_sh_flags in metric_sh_flags_list:
                    if ((section['sh_flags'] == metric_sh_flags)
                            and (section['sh_type'] == metric_sh_type)):
                        sec_sizes[metric] += section['sh_size']
        for metric, size in dummy_sec_sizes.items():
            if metric in metrics:
                sec_sizes[metric] -= size

    # Return the section (group) size
    return sec_sizes


def get_dummy_data():
    """Get the ELF section size data for the dummy benchmark and return it."""
    if isinstance(gp['dummy_benchmark'], str):
        dummy_section_data = benchmark_size(gp['dummy_benchmark'],
                                            gp['bd_supportdir'], ALL_METRICS,
                                            {})
    else:
        dummy_section_data = {}
    if not dummy_section_data:
        dummy_benchmark_abs_path = os.path.join(gp['bd_supportdir'],
                                                gp['dummy_benchmark'])
        log.error(
            f'ERROR: could not find dummy benchmark at {dummy_benchmark_abs_path}'
        )
        sys.exit(1)
    return dummy_section_data


def output_json(benchmarks, raw_totals, rel_data):
    """Output the results in JSON format."""
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

    if gp['absolute']:
        log.info('    }')
        log.info('  }')
        log.info('}')
    else:
        log.info('    }')
        log.info('  },')


def output_text(benchmarks, raw_totals, rel_data):
    """Output the results in plain text format."""
    log.info('Benchmark            size')
    log.info('---------            ----')

    for bench in benchmarks:
        res_output = ''
        if gp['absolute']:
            res_output = f' {raw_totals[bench]:8,}'
        else:
            res_output = f'   {rel_data[bench]:6.2f}'
        log.info(f'{bench:15} {res_output:8}')


def output_md(benchmarks, raw_totals, rel_data):
    """Output the results in MarkDown format."""
    log.info('| Benchmark         |     Size |')
    log.info('| :---------------- | -------: |')

    for bench in benchmarks:
        res_output = ''
        md_bench = '`' + bench + '`'
        if gp['absolute']:
            res_output = f'{raw_totals[bench]:8}'
        else:
            res_output = f'{rel_data[bench]:8.2f}'
        log.info(f'| {md_bench:17} | {res_output:8} |')


def output_csv(benchmarks, raw_totals, rel_data):
    """Output the results in CSV format."""
    log.info('"Benchmark","Size"')

    for bench in benchmarks:
        res_output = ''
        if gp['absolute']:
            res_output = f'{raw_totals[bench]:0}'
        else:
            res_output = f'{rel_data[bench]:.2f}'
        log.info(f'"{bench}","{res_output}"')


def output_baseline(benchmarks, raw_section_data):
    """Output the results in suitable as baseline data."""
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
    with open(size_baseline, "rb") as fileh:
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

    # Collect dummy section sizes
    dummy_section_data = get_dummy_data()

    # Measure each benchmark, subtracting the dummy section sizes
    for bench in benchmarks:
        if gp['output_format'] == output_format.BASELINE:
            raw_section_data[bench] = benchmark_size(bench, gp['bd_benchdir'],
                                                     ALL_METRICS,
                                                     dummy_section_data)
        else:
            raw_section_data[bench] = benchmark_size(bench, gp['bd_benchdir'],
                                                     gp['metric'],
                                                     dummy_section_data)
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
        output_json(benchmarks, raw_totals, rel_data)
    elif gp['output_format'] == output_format.TEXT:
        output_text(benchmarks, raw_totals, rel_data)
    elif gp['output_format'] == output_format.MD:
        output_md(benchmarks, raw_totals, rel_data)
    elif gp['output_format'] == output_format.CSV:
        output_csv(benchmarks, raw_totals, rel_data)
    elif gp['output_format'] == output_format.BASELINE:
        output_baseline(benchmarks, raw_section_data)

    if successful:
        return raw_totals, rel_data

    # Otherwise failure return
    return [], []


def output_stats_json(geomean, geosd, georange):
    """Output the stats in JSON format."""
    log.info(f'  "geomean" : {geomean:.2f},')
    log.info(f'  "geosd" : {geosd:.2f},')
    log.info(f'  "georange" : {georange:.2f}')

    log.info('}')


def output_stats_text(geomean, geosd, georange):
    """Output the stats in plain text format."""
    log.info('---------------  --------')
    log.info(f'Geometric mean   {geomean:8.2f}')
    log.info(f'Geometric s.d.   {geosd:8.2f}')
    log.info(f'Geometric range  {georange:8.2f}')


def output_stats_md(geomean, geosd, georange):
    """Output the stats in MarkDown format."""
    log.info('|                   |          |')
    log.info(f'| Geometric mean    | {geomean:8.2f} |')
    log.info(f'| Geometric s.d.    | {geosd:8.2f} |')
    log.info(f'| Geometric range   | {georange:8.2f} |')


def output_stats_csv(geomean, geosd, georange):
    """Output the stats in CSV format."""
    log.info('"",""')
    log.info(f'"Geometric mean","{geomean:.2f}"')
    log.info(f'"Geometric s.d.","{geosd:.2f}"')
    log.info(f'"Geometric range","{georange:.2f}"')


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
        if not gp['absolute']:
            geomean, geosd, georange = embench_stats(benchmarks, raw_data,
                                                     rel_data)
            if gp['output_format'] == output_format.JSON:
                output_stats_json(geomean, geosd, georange)
            elif gp['output_format'] == output_format.TEXT:
                output_stats_text(geomean, geosd, georange)
            elif gp['output_format'] == output_format.MD:
                output_stats_md(geomean, geosd, georange)
            elif gp['output_format'] == output_format.CSV:
                output_stats_csv(geomean, geosd, georange)
    else:
        log.info('ERROR: Failed to compute size benchmarks')
        sys.exit(1)


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
