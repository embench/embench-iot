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
import shutil
import subprocess
import sys
import time
import traceback

from elftools.elf.elffile import ELFFile

# Reference data

baseline = {
    'aha-mont64' : {
        'text' : 1052,
        'rodata' : 0,
        'data' : 0,
        'bss' : 0
    },
    'crc32' : {
        'text' : 230,
        'rodata' : 1024,
        'data' : 0,
        'bss' : 0
    },
    'cubic' : {
        'text' : 2472,
        'rodata' : 0,
        'data' : 0,
        'bss' : 24
    },
    'edn' : {
        'text' : 1452,
        'rodata' : 1600,
        'data' : 0,
        'bss' : 1600
    },
    'huffbench' : {
        'text' : 1628,
        'rodata' : 1004,
        'data' : 0,
        'bss' : 8692
    },
    'matmult-int' : {
        'text' : 420,
        'rodata' : 1600,
        'data' : 0,
        'bss' : 8004
    },
    'minver' : {
        'text' : 1076,
        'rodata' : 144,
        'data' : 0,
        'bss' : 108
    },
    'nbody' : {
        'text' : 708,
        'rodata' : 320,
        'data' : 320,
        'bss' : 0
    },
    'nettle-aes' : {
        'text' : 2880,
        'rodata' : 10022,
        'data' : 544,
        'bss' : 1000
    },
    'nettle-sha256' : {
        'text' : 5564,
        'rodata' : 448,
        'data' : 88,
        'bss' : 32
    },
    'nsichneu' : {
        'text' : 15042,
        'rodata' : 0,
        'data' : 0,
        'bss' : 56
    },
    'picojpeg' : {
        'text' : 8036,
        'rodata' : 1196,
        'data' : 0,
        'bss' : 2320
    },
    'qrduino' : {
        'text' : 6074,
        'rodata' : 1540,
        'data' : 0,
        'bss' : 8232
    },
    'sglib-combined' : {
        'text' : 2324,
        'rodata' : 800,
        'data' : 0,
        'bss' : 8676
    },
    'slre' : {
        'text' : 2428,
        'rodata' : 64,
        'data' : 62,
        'bss' : 16
    },
    'st' : {
        'text' : 880,
        'rodata' : 0,
        'data' : 0,
        'bss' : 1632
    },
    'statemate' : {
        'text' : 3692,
        'rodata' : 64,
        'data' : 0,
        'bss' : 292
    },
    'ud' : {
        'text' : 702,
        'rodata' : 0,
        'data' : 0,
        'bss' : 1764
    },
    'wikisort' : {
        'text' : 4214,
        'rodata' : 3236,
        'data' : 0,
        'bss' : 3200
    }
}

# Handle for the logger
log = logging.getLogger()

# All the global parameters
gp = dict()

# All the benchmarks
benchmarks = []


def build_parser():
    """Build a parser for all the arguments"""
    parser = argparse.ArgumentParser(
        description='Compute the size benchmark')

    parser.add_argument(
        '--builddir', type=str, default='bd',
        help='Directory holding all the binaries'
    )
    parser.add_argument(
        '--logdir', type=str, default='logs',
        help='Directory in which to store logs',
    )
    parser.add_argument(
        '--absolute', action='store_true',
        help='Specify to show absolute results',
    )

    return parser


def create_logdir(logdir):
    """Create the log directory, which can be relative to the current directory
       or absolute"""
    if not os.path.isabs(logdir):
        logdir = os.path.join (gp['rootdir'], logdir)

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
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    log.addHandler(ch)
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    log.addHandler(fh)


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
        gp['bd'] = builddir
    else:
        gp['bd'] = os.path.join(gp['rootdir'], args.builddir)

    if not os.path.isdir(gp['bd']):
        log.error(f'ERROR: build directory {gp["bd"]} not found: exiting')
        sys.exit(1)

    if not os.access(gp['bd'], os.R_OK):
        log.error(f'ERROR: Unable to read build directory {gp["bd"]}: exiting')
        sys.exit(1)


def find_benchmarks():
    """Enumerate all the built benchmarks in alphabetical order into the global
       variable, 'benchmarks'. The benchmarks are found in the 'src'
       subdirectory of the benchmarks repo."""
    gp['bd_benchdir'] = os.path.join(gp['bd'], 'src')
    dirlist = os.listdir(gp['bd_benchdir'])

    benchmarks.clear()

    for b in dirlist:
        abs_b_dir = os.path.join(gp['bd_benchdir'], b)
        abs_b = os.path.join(abs_b_dir, b)
        # Must be a directory - ignore anything else
        if os.path.isdir(abs_b_dir):
            if os.path.isfile(abs_b):
                benchmarks.append(b)
            else:
                log.warning(f'WARNING: Binary not found for benchmark "{b}"')

    benchmarks.sort()


def log_benchmarks():
    """Record all the benchmarks in the log"""
    log.debug('Benchmarks')
    log.debug('==========')

    for b in benchmarks:
        log.debug(b)

    log.debug('')


def get_section(elf, section_name):
    # Workaround to use get_section_by_name on pyelftools both pre- and post-
    # version 0.24 - section names are always decoded in 0.24 onwards
    section = elf.get_section_by_name(section_name)
    if section:
        return section
    encoded_name = codecs.encode(section_name, 'utf-8')
    return elf.get_section_by_name(encoded_name)


def benchmark_size(b):
    """Compute the sizes of the key sections in a benchmark.  Returns a list
       with the size of .text, .rodata, .data and .bss."""
    appexe = os.path.join(gp['bd_benchdir'], b, b)

    with open(appexe, 'rb') as f:
        elf = ELFFile(f)

        text = get_section(elf, '.text')
        if text is None:
            log.warning('Warning: .text section not found in benchmark "{b}"')
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

        return { 'text'   : text_size,
                 'rodata' : rodata_size,
                 'data'   : data_size,
                 'bss'    : bss_size }


def main():
    """Main program driving measurement of benchmark size"""
    # Establish the root directory of the repository, since we know this file is
    # in that directory.
    gp['rootdir'] = os.path.abspath(os.path.dirname(__file__))

    # Parse arguments using standard technology
    parser = build_parser()
    args   = parser.parse_args()

    # Establish logging
    logdir  = create_logdir(args.logdir)
    logfile = os.path.join(logdir, time.strftime('size-%Y-%m-%d-%H%M%S.log'))
    setup_logging(logfile)
    log_args(args)
    log.debug(f'Log file:        {logfile}\n')

    # Check args are OK (have to have logging and build directory set up first)
    validate_args(args)

    # Find the benchmarks
    find_benchmarks()
    log_benchmarks()

    # We can't compute geometric SD on the fly, so we need to collect all the
    # data and then process it in two passes. We could do the first processing
    # as we collect the data, but it is clearer to do the three things
    # separately. Given the size of datasets with which we are concerned the
    # compute overhead is not significant.

    # Collect data and output it

    successful = True
    raw_data = {}
    rel_data = {}
    log.info('Benchmark            Text  R/O Data      Data       BSS')
    log.info('---------            ----  --------      ----       ---')

    for b in benchmarks:
        raw_data[b] = benchmark_size(b)
        rel_data[b] = {}
        if raw_data[b]['text'] == 0:
            del raw_data[b]
            del rel_data[b]
            successful = False
        else:
            output = {}
            if args.absolute:
                # Want absolute results. Only include non-zero values
                for v in { 'text', 'rodata', 'data', 'bss' } :
                    if raw_data[b][v] > 0:
                        output[v] = f'{raw_data[b][v]:8,}'
                    else:
                        del raw_data[b][v]
                        output[v] = '       0'
            else:
                # Want relative results (the default). Only use non-zero values.
                for v in { 'text', 'rodata', 'data', 'bss' } :
                    if (baseline[b][v] > 0) and (raw_data[b][v] > 0):
                        rel_data[b][v] = raw_data[b][v] / baseline[b][v]
                        output[v] = f'  {rel_data[b][v]:6.2f}'
                    else:
                        output[v] = ' -   '
            log.info(
                f'{b:15}  {output["text"]:8}  {output["rodata"]:8}  ' +
                f'{output["data"]:8}  {output["bss"]:8}'
            )

    # Compute geometric mean
    geomean = { 'text' : 1.0, 'rodata' : 1.0, 'data' : 1.0, 'bss' : 1.0 }
    count   = { 'text' : 0.0, 'rodata' : 0.0, 'data' : 0.0, 'bss' : 0.0 }

    for b in benchmarks:
        if args.absolute:
            # Want absolute results
            if b in raw_data:
                for v in { 'text', 'rodata', 'data', 'bss' } :
                    if v in raw_data[b]:
                        count[v] += 1
                        geomean[v] *= raw_data[b][v]
        else:
            # Want relative results (the default).
            if b in rel_data:
                for v in { 'text', 'rodata', 'data', 'bss' } :
                    if v in rel_data[b]:
                        count[v] += 1
                        geomean[v] *= rel_data[b][v]

    for v in { 'text', 'rodata', 'data', 'bss' } :
        if count[v] > 0:
            geomean[v] = pow(geomean[v], 1.0 / count[v])

    # Compute geometric SD
    lnsize = { 'text' : 0.0, 'rodata' : 0.0, 'data' : 0.0, 'bss' : 0.0 }
    geosd  = {}

    for b in benchmarks:
        if args.absolute:
            # Want absolute results
            if b in raw_data:
                for v in { 'text', 'rodata', 'data', 'bss' } :
                    if v in raw_data[b]:
                        lnsize[v] += math.pow(
                            math.log(raw_data[b][v] / geomean[v]), 2
                        )
        else:
            # Want relative results (the default).
            if b in rel_data:
                for v in { 'text', 'rodata', 'data', 'bss' } :
                    if v in rel_data[b]:
                        lnsize[v] += math.pow(
                            math.log(rel_data[b][v] / geomean[v]), 2
                        )

    for v in { 'text', 'rodata', 'data', 'bss' } :
        if count[v] > 0:
            geosd[v]      = math.exp(math.sqrt(lnsize[v] / count[v]))

    # Do the math
    range = {}
    geomean_op = {}
    geosd_op   = {}
    range_op   = {}

    for v in { 'text', 'rodata', 'data', 'bss' } :
        if count[v] > 0 :
            if geosd[v] > 0.0:
                range[v] = geomean[v] * geosd[v] - geomean[v] / geosd[v]
            else:
                range[v] = 0.0
            if args.absolute:
                geomean_op[v] = f'{round(geomean[v]):8,}'
                geosd_op[v]   = f'  {(geosd[v]):6.2f}'
                range_op[v]   = f'{round(range[v]):8,}'
            else:
                geomean_op[v] = f'  {geomean[v]:6.2f}'
                geosd_op[v]   = f'  {geosd[v]:6.2f}'
                range_op[v]   = f'  {range[v]:6.2f}'
        else:
            geomean_op[v] = ' -   '
            geosd_op[v]   = ' -   '
            range_op[v]   = ' -    '

    # Output the results
    log.info('---------            ----  --------      ----       ---')
    log.info(f'Geometric mean   {geomean_op["text"]:8}  ' +
             f'{geomean_op["rodata"]:8}  {geomean_op["data"]:8}  ' +
             f'{geomean_op["bss"]:8}')
    log.info(f'Geometric SD     {geosd_op["text"]:8}  ' +
             f'{geosd_op["rodata"]:8}  {geosd_op["data"]:8}  ' +
             f'{geosd_op["bss"]:8}')
    log.info(f'Geometric range  {range_op["text"]:8}  ' +
             f'{range_op["rodata"]:8}  {range_op["data"]:8}  ' +
             f'{range_op["bss"]:8}')

    if successful:
        log.info('All benchmarks sized successfully')

# Only run if this is the main package

if __name__ == '__main__':
    sys.exit(main())
