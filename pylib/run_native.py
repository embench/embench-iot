#!/usr/bin/env python3

# Python module to run programs natively.

# Copyright (C) 2019 Clemson University
#
# Contributor: Ola Jeppsson <ola.jeppsson@gmail.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Embench module to run benchmark programs.

This version is suitable for running programs natively.
"""

import argparse
import subprocess
import re

from embench_core import log


def get_target_args(remnant):
    """Parse left over arguments"""
    parser = argparse.ArgumentParser(description='Get target specific args')

    # No target arguments
    return parser.parse_args(remnant)

def decode_results(stdout_str, stderr_str):
    """Extract the results from the output string of the run. Return the
       elapsed time in milliseconds or zero if the run failed."""
    # See above in build_benchmark_cmd how we record the return value and
    # execution time. Return code is in standard output. Execution time is in
    # standard error.

    # Match "RET=rc"
    rcstr = re.search('^RET=(\d+)', stdout_str, re.S | re.M)
    if not rcstr:
        log.debug('Warning: Failed to find return code')
        return None

    # Match "real s.mm?m?"
    time = re.search('^real (\d+)[.](\d+)', stderr_str, re.S)
    if time:
        ms_elapsed = int(time.group(1)) * 1000 + \
                     int(time.group(2).ljust(3,'0')) # 0-pad
        # Return value cannot be zero (will be interpreted as error)
        return max(float(ms_elapsed), 0.001)

    # We must have failed to find a time
    log.debug('Warning: Failed to find timing')
    return None

def run_benchmark(bench, path, args):
    """Runs the benchmark "bench" at "path". "args" is a namespace
       with target specific arguments. This function will be called
       in parallel unless if the number of tasks is limited via
       command line. "run_benchmark" should return the result in
       milliseconds.
    """

    try:
        res = subprocess.run(
            ['sh', '-c', 'time -p ' + path + '; echo RET=$?'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=50,
        )
    except subprocess.TimeoutExpired:
        log.warning(f'Warning: Run of {bench} timed out.')
        return None
    if res.returncode != 0:
        return None
    return decode_results(res.stdout.decode('utf-8'), res.stderr.decode('utf-8'))
