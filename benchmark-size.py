#!/usr/bin/env python3

# Script to benchmark size

# Copyright (C) 2017, 2019 Embecosm Limited
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import codecs
import logging
import math
import os
import sys
import time

from json import loads
from elftools.elf.elffile import ELFFile


# Handle for the logger
log = logging.getLogger()

# All the global parameters
gp = dict()


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


def create_logdir(logdir):
    """Create the log directory, which can be relative to the current directory
       or absolute"""
    if not os.path.isabs(logdir):
        logdir = os.path.join(gp['rootdir'], logdir)

    if not os.path.isdir(logdir):
        try:
            os.makedirs(logdir)
        except PermissionError:
            raise PermissionError(f'Unable to create log directory {logdir}')

    if not os.access(logdir, os.W_OK):
        raise PermissionError(f'Unable to write to log directory {logdir}')

    return logdir


def setup_logging(logfile):
    """Set up logging. Debug messages only go to file, everything else
       also goes to the console."""
    log.setLevel(logging.DEBUG)
    cons_h = logging.StreamHandler(sys.stdout)
    cons_h.setLevel(logging.INFO)
    log.addHandler(cons_h)
    file_h = logging.FileHandler(logfile)
    file_h.setLevel(logging.DEBUG)
    log.addHandler(file_h)


def log_args(args):
    """Record all the argument values"""
    log.debug('Supplied arguments')
    log.debug('==================')
    log.debug(f'Build directory:      {args.builddir}')
    log.debug(f'Log directory:        {args.logdir}')
    log.debug('')


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


def find_benchmarks():
    """Enumerate all the benchmarks in alphabetical order into the global
       variable, 'benchmarks'. The benchmarks are found in the 'src'
       subdirectory of the benchmarks repo.

       Return the list of benchmarks."""
    gp['benchdir'] = os.path.join(gp['rootdir'], 'src')
    gp['bd_benchdir'] = os.path.join(gp['bd'], 'src')
    dirlist = os.listdir(gp['benchdir'])

    benchmarks = []

    for bench in dirlist:
        abs_b = os.path.join(gp['benchdir'], bench)
        if os.path.isdir(abs_b):
            benchmarks.append(bench)

    benchmarks.sort()

    return benchmarks


def log_benchmarks(benchmarks):
    """Record all the benchmarks in the log"""
    log.debug('Benchmarks')
    log.debug('==========')

    for bench in benchmarks:
        log.debug(bench)

    log.debug('')


def get_section(elf, section_name):
    """Workaround to use get_section_by_name on pyelftools both pre- and post-
       version 0.24 - section names are always decoded in 0.24 onwards"""
    section = elf.get_section_by_name(section_name)
    if section:
        return section
    encoded_name = codecs.encode(section_name, 'utf-8')
    return elf.get_section_by_name(encoded_name)


def benchmark_size(bench):
    """Compute the sizes of the key sections in a benchmark.  Returns a list
       with the size of .text, .rodata, .data and .bss."""
    appexe = os.path.join(gp['bd_benchdir'], bench, bench)

    with open(appexe, 'rb') as fileh:
        elf = ELFFile(fileh)

        text = get_section(elf, '.text')
        if text is None:
            log.warning(
                'Warning: .text section not found in benchmark "{bench}"'
            )
            text_size = 0
        else:
            text_size = text['sh_size']

        rodata = get_section(elf, '.rodata')
        if rodata is None:
            rodata_size = 0
        else:
            rodata_size = rodata['sh_size']

        data = get_section(elf, '.data')
        if data is None:
            data_size = 0
        else:
            data_size = data['sh_size']

        bss = get_section(elf, '.bss')
        if bss is None:
            bss_size = 0
        else:
            bss_size = bss['sh_size']

        return {
            'text': text_size,
            'rodata': rodata_size,
            'data': data_size,
            'bss': bss_size,
        }


def collect_data(benchmarks):
    """Collect and log all the raw and optionally relative data associated with
       the list of benchmarks supplied in the "benchmarks" argument. Return
       the raw data and relative data as a list.  The raw data may be empty if
       there is a failure. The relative data will be empty if only absolute
       results have been requested."""

    # Baseline data is held external to the script. Import it here.
    gp['baseline_dir'] = os.path.join(gp['rootdir'], 'baseline-size.json')
    with open(gp['baseline_dir']) as fileh:
        baseline = loads(fileh.read())

    # Collect data and output it
    successful = True
    raw_data = {}
    rel_data = {}
    log.info('Benchmark            Text  R/O Data      Data       BSS')
    log.info('---------            ----  --------      ----       ---')

    for bench in benchmarks:
        raw_data[bench] = benchmark_size(bench)
        rel_data[bench] = {}
        if raw_data[bench]['text'] == 0:
            del raw_data[bench]
            del rel_data[bench]
            successful = False
        else:
            output = {}
            if gp['absolute']:
                # Want absolute results. Only include non-zero values
                for sec in {'text', 'rodata', 'data', 'bss'}:
                    have_benchmark_data = raw_data[bench][sec] > 0
                    if have_benchmark_data:
                        output[sec] = f'{raw_data[bench][sec]:8,}'
                    else:
                        del raw_data[bench][sec]
                        output[sec] = '       0'
            else:
                # Want relative results (the default). Only use non-zero values.
                for sec in ['text', 'rodata', 'data', 'bss']:
                    have_baseline_data = baseline[bench][sec] > 0
                    have_benchmark_data = raw_data[bench][sec] > 0
                    if have_baseline_data and have_benchmark_data:
                        rel_data[bench][sec] = (
                            raw_data[bench][sec] / baseline[bench][sec]
                        )
                        output[sec] = f'  {rel_data[bench][sec]:6.2f}'
                    else:
                        output[sec] = ' -   '
            log.info(
                f'{bench:15}  {output["text"]:8}  {output["rodata"]:8}  '
                + f'{output["data"]:8}  {output["bss"]:8}'
            )

    if successful:
        return raw_data, rel_data

    # Otherwise failure return
    return [], []


def compute_geomean(benchmarks, raw_data, rel_data):
    """Compute the geometric mean and count the number of data points for the
       supplied benchmarks, raw and optionally relative data. Return a
       dictionary of geometric mean data and a dictionary of count data, with a
       entry for each section type."""

    geomean = {'text': 1.0, 'rodata': 1.0, 'data': 1.0, 'bss': 1.0}
    count = {'text': 0.0, 'rodata': 0.0, 'data': 0.0, 'bss': 0.0}

    for bench in benchmarks:
        if gp['absolute']:
            # Want absolute results
            if bench in raw_data:
                for sec in ['text', 'rodata', 'data', 'bss']:
                    if sec in raw_data[bench]:
                        count[sec] += 1
                        geomean[sec] *= raw_data[bench][sec]
        else:
            # Want relative results (the default).
            if bench in rel_data:
                for sec in ['text', 'rodata', 'data', 'bss']:
                    if sec in rel_data[bench]:
                        count[sec] += 1
                        geomean[sec] *= rel_data[bench][sec]

    for sec in ['text', 'rodata', 'data', 'bss']:
        if count[sec] > 0:
            geomean[sec] = pow(geomean[sec], 1.0 / count[sec])

    return geomean, count


def compute_geosd(benchmarks, raw_data, rel_data, geomean, count):
    """Compute geometric standard deviation for the given set of benchmarks,
       using the supplied raw and optinally relative data. This draws on the
       previously computed geometric mean and count for each benchmark.

       Return a set of geometric standard deviations for each section type."""
    lnsize = {'text': 0.0, 'rodata': 0.0, 'data': 0.0, 'bss': 0.0}
    geosd = {}

    for bench in benchmarks:
        if gp['absolute']:
            # Want absolute results
            if bench in raw_data:
                for sec in ['text', 'rodata', 'data', 'bss']:
                    if sec in raw_data[bench]:
                        lnsize[sec] += math.pow(
                            math.log(raw_data[bench][sec] / geomean[sec]), 2
                        )
        else:
            # Want relative results (the default).
            if bench in rel_data:
                for sec in ['text', 'rodata', 'data', 'bss']:
                    if sec in rel_data[bench]:
                        lnsize[sec] += math.pow(
                            math.log(rel_data[bench][sec] / geomean[sec]), 2
                        )

    # Compute the standard deviation using the lnsize data for each benchmark.
    for sec in ['text', 'rodata', 'data', 'bss']:
        if count[sec] > 0:
            geosd[sec] = math.exp(math.sqrt(lnsize[sec] / count[sec]))

    return geosd


def compute_georange(geomean, geosd, count):
    """Compute the geometric range of one geometric standard deviation around
       the geometric mean for each section type.  Return a set of data for
       each section type"""

    georange = {}

    for sec in ['text', 'rodata', 'data', 'bss']:
        if count[sec] > 0:
            if geosd[sec] > 0.0:
                georange[sec] = (
                    geomean[sec] * geosd[sec] - geomean[sec] / geosd[sec]
                )
            else:
                georange[sec] = 0.0

    return georange


def output_stats(geomean, geosd, georange, count):
    """Output the statistical summary for each seciton type."""
    geomean_op = {}
    geosd_op = {}
    georange_op = {}

    for sec in ['text', 'rodata', 'data', 'bss']:
        if count[sec] > 0:
            if gp['absolute']:
                geomean_op[sec] = f'{round(geomean[sec]):8,}'
                geosd_op[sec] = f'  {(geosd[sec]):6.2f}'
                georange_op[sec] = f'{round(georange[sec]):8,}'
            else:
                geomean_op[sec] = f'  {geomean[sec]:6.2f}'
                geosd_op[sec] = f'  {geosd[sec]:6.2f}'
                georange_op[sec] = f'  {georange[sec]:6.2f}'
        else:
            geomean_op[sec] = ' -   '
            geosd_op[sec] = ' -   '
            georange_op[sec] = ' -    '

    # Output the results
    log.info('---------            ----  --------      ----       ---')
    log.info(
        f'Geometric mean   {geomean_op["text"]:8}  '
        + f'{geomean_op["rodata"]:8}  {geomean_op["data"]:8}  '
        + f'{geomean_op["bss"]:8}'
    )
    log.info(
        f'Geometric SD     {geosd_op["text"]:8}  '
        + f'{geosd_op["rodata"]:8}  {geosd_op["data"]:8}  '
        + f'{geosd_op["bss"]:8}'
    )
    log.info(
        f'Geometric range  {georange_op["text"]:8}  '
        + f'{georange_op["rodata"]:8}  {georange_op["data"]:8}  '
        + f'{georange_op["bss"]:8}'
    )


def main():
    """Main program driving measurement of benchmark size"""
    # Establish the root directory of the repository, since we know this file is
    # in that directory.
    gp['rootdir'] = os.path.abspath(os.path.dirname(__file__))

    # Parse arguments using standard technology
    parser = build_parser()
    args = parser.parse_args()

    # Establish logging
    logdir = create_logdir(args.logdir)
    logfile = os.path.join(logdir, time.strftime('size-%Y-%m-%d-%H%M%S.log'))
    setup_logging(logfile)
    log_args(args)
    log.debug(f'Log file:        {logfile}\n')

    # Check args are OK (have to have logging and build directory set up first)
    validate_args(args)

    # Find the benchmarks
    benchmarks = find_benchmarks()
    log_benchmarks(benchmarks)

    # We can't compute geometric SD on the fly, so we need to collect all the
    # data and then process it in two passes. We could do the first processing
    # as we collect the data, but it is clearer to do the three things
    # separately. Given the size of datasets with which we are concerned the
    # compute overhead is not significant.

    raw_data, rel_data = collect_data(benchmarks)
    if raw_data:
        geomean, count = compute_geomean(benchmarks, raw_data, rel_data)
        geosd = compute_geosd(benchmarks, raw_data, rel_data, geomean, count)
        georange = compute_georange(geomean, geosd, count)
        output_stats(geomean, geosd, georange, count)
        log.info('All benchmarks sized successfully')
    else:
        log.info('ERROR: Failed to compute size benchmarks')
        sys.exit(1)


# Only run if this is the main package

if __name__ == '__main__':
    sys.exit(main())
