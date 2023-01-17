#!/usr/bin/env python3

# Python module to run programs natively.

# Copyright (C) 2019 Clemson University
# Copyright (C) 2023 University of Bremen
#
# Contributor: Ola Jeppsson <ola.jeppsson@gmail.com>
# Contributor Sören Tempel <tempel@uni-bremen.de>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Embench module to run benchmark programs.

This version is suitable for running programs within a simulator.
"""

__all__ = [
    'get_target_args',
    'build_benchmark_cmd',
    'decode_results',
]

import argparse
import re

from run_native import decode_results
from embench_core import log


def get_target_args(remnant):
    """Parse left over arguments"""
    parser = argparse.ArgumentParser(description='Get target specific args')
    parser.add_argument(
        '--simulator',
        type=str,
        help='Simulator command to run benchmarks with'
    )

    # No target arguments
    return parser.parse_args(remnant)


def build_benchmark_cmd(bench, args):
    """Construct the command to run the benchmark.  "args" is a
       namespace with target specific arguments"""
    simulator = args.simulator

    # Due to way the target interface currently works we need to construct
    # a command that records both the return value and execution time to
    # stdin/stdout. Obviously using time will not be very precise.
    return ['sh', '-c', f'time -p {simulator} ./' + bench + '; echo RET=$?']
