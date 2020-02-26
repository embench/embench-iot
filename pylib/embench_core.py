#!/usr/bin/env python3

# Common python procedures for use across Embench.

# Copyright (C) 2017, 2019 Embecosm Limited
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Embench common procedures.

This version is suitable when using a version of GDB which can launch a GDB
server to use as a target.
"""

import logging
import math
import os
import re
import sys
import time


# What we export

__all__ = [
    'check_python_version',
    'log',
    'gp',
    'setup_logging',
    'log_args',
    'log_benchmarks',
    'embench_stats',
    'arglist_to_str',
]

# Handle for the logger
log = logging.getLogger()

# All the global parameters
gp = dict()


# Make sure we have new enough python
def check_python_version(major, minor):
    """Check the python version is at least {major}.{minor}."""
    if ((sys.version_info[0] < major)
        or ((sys.version_info[0] == major) and (sys.version_info[1] < minor))):
        log.error(f'ERROR: Requires Python {major}.{minor} or later')
        sys.exit(1)


def create_logdir(logdir):
    """Create the log directory, which can be relative to the root directory
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


def setup_logging(logdir, prefix):
    """Set up logging in the directory specified by "logdir".

       The log file name is the "prefix" argument followed by a timestamp.

       Debug messages only go to file, everything else also goes to the
       console."""

    # Create the log directory first if necessary.
    logdir_abs = create_logdir(logdir)
    logfile = os.path.join(
        logdir_abs, time.strftime(f'{prefix}-%Y-%m-%d-%H%M%S.log')
    )

    # Set up logging
    log.setLevel(logging.DEBUG)
    cons_h = logging.StreamHandler(sys.stdout)
    cons_h.setLevel(logging.INFO)
    log.addHandler(cons_h)
    file_h = logging.FileHandler(logfile)
    file_h.setLevel(logging.DEBUG)
    log.addHandler(file_h)

    # Log where the log file is
    log.debug(f'Log file: {logfile}\n')
    log.debug('')


def log_args(args):
    """Record all the argument values"""
    log.debug('Supplied arguments')
    log.debug('==================')

    for arg in vars(args):
        realarg = re.sub('_', '-', arg)
        val = getattr(args, arg)
        log.debug(f'--{realarg:20}: {val}')

    log.debug('')


def find_benchmarks():
    """Enumerate all the benchmarks in alphabetical order.  The benchmarks are
       found in the 'src' subdirectory of the root directory.  Set up global
       parameters for the source and build benchmark directories.

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


def compute_geomean(benchmarks, raw_data, rel_data):
    """Compute the geometric mean and count the number of data points for the
       supplied benchmarks, raw and optionally relative data. Return a
       list of geometric mean and count of data, with a."""

    geomean = 1.0
    count = 0.0

    for bench in benchmarks:
        if gp['absolute']:
            # Want absolute results. Ignore zero values
            if bench in raw_data:
                if raw_data[bench] > 0:
                    count += 1
                    geomean *= raw_data[bench]
        else:
            # Want relative results (the default). Ignore zero value
            if bench in rel_data:
                if rel_data[bench] > 0:
                    count += 1
                    geomean *= rel_data[bench]

    if count > 0.0:
        geomean = pow(geomean, 1.0 / count)

    return geomean, count


def compute_geosd(benchmarks, raw_data, rel_data, geomean, count):
    """Compute geometric standard deviation for the given set of benchmarks,
       using the supplied raw and optinally relative data. This draws on the
       previously computed geometric mean and count for each benchmark.

       Return geometric standard deviation."""
    lnsize = 0.0
    geosd = 0.0

    for bench in benchmarks:
        if gp['absolute']:
            # Want absolute results
            if raw_data[bench] > 0.0:
                lnsize += math.pow(math.log(raw_data[bench] / geomean), 2)
        else:
            # Want relative results (the default).
            if rel_data[bench] > 0.0:
                lnsize += math.pow(math.log(rel_data[bench] / geomean), 2)

    # Compute the standard deviation using the lnsize data for each benchmark.
    if count > 0.0:
        geosd = math.exp(math.sqrt(lnsize / count))

    return geosd


def compute_georange(geomean, geosd, count):
    """Compute the geometric range of one geometric standard deviation around
       the geometric mean.  Return the geometric range."""

    georange = 0.0

    if count > 0:
        if geosd > 0.0:
            georange = geomean * geosd - geomean / geosd
        else:
            georange = 0.0

    return georange


def output_stats(geomean, geosd, georange, count, bm_type, opt_comma):
    """Output the statistical summary.

       Note that we manually generate the JSON output, rather than using the
       dumps method, because the result will be manually edited, and we want
       to guarantee the layout."""

    geomean_op = ''
    geosd_op = ''
    georange_op = ''

    if count > 0:
        if gp['absolute']:
            if gp['json']:
                geomean_op = f'{round(geomean)}'
                geosd_op = f'{(geosd):.2f}'
            else:
                geomean_op = f'{round(geomean):8,}'
                geosd_op = f'     {(geosd):6.2f}'

            georange_op = f'{round(georange):8,}'
        else:
            if gp['json']:
                geomean_op = f'{geomean:.2f}'
                geosd_op = f'{geosd:.2f}'
            else:
                geomean_op = f'  {geomean:6.2f}'
                geosd_op = f'  {geosd:6.2f}'

            georange_op = f'  {georange:6.2f}'
    else:
        geomean_op = ' -   '
        geosd_op = ' -   '
        georange_op = ' -    '

    # Output the results
    if gp['json']:
        log.info(f'    "{bm_type} geometric mean" : {geomean_op},')
        log.info(f'    "{bm_type} geometric standard deviation" : {geosd_op}')
        log.info('  }' + f'{opt_comma}')
    else:
        log.info('---------           -----')
        log.info(f'Geometric mean   {geomean_op:8}')
        log.info(f'Geometric SD     {geosd_op:8}')
        log.info(f'Geometric range  {georange_op:8}')


def embench_stats(benchmarks, raw_data, rel_data, bm_type, opt_comma):
    """Output statistics summary for Embench."""
    geomean, count = compute_geomean(benchmarks, raw_data, rel_data)
    geosd = compute_geosd(benchmarks, raw_data, rel_data, geomean, count)
    georange = compute_georange(geomean, geosd, count)
    output_stats(geomean, geosd, georange, count, bm_type, opt_comma)


def arglist_to_str(arglist):
    """Make arglist into a string"""

    for arg in arglist:
        if arg == arglist[0]:
            str = arg
        else:
            str = str + ' ' + arg

    return str
