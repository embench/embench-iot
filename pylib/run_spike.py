#!/usr/bin/env python3

# Python module to run programs with RISC-V ISA simulator spike.

# Copyright (C) 2023 HighTec edV-Systeme GmbH
#
# Contributor: Emil J. Tywoniak <emil.tywoniak@gmail.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Embench module to run benchmark programs.

This version is suitable for running programs with RISC-V ISA simulator spike.
"""

__all__ = [
    'get_target_args',
    'build_benchmark_cmd',
    'decode_results',
]

import argparse
import re

from embench_core import log


def get_target_args(remnant):
    """Parse left over arguments"""
    parser = argparse.ArgumentParser(description='Get target specific args')

    # No target arguments
    return parser.parse_args(remnant)


def build_benchmark_cmd(bench, args):
    """Construct the command to run the benchmark.  "args" is a
       namespace with target specific arguments"""

    # Due to way the target interface currently works we need to construct
    # a command that records both the return value and execution time to
    # stdin/stdout. Obviously using time will not be very precise.
    # Hacky workaround for https://github.com/riscv-software-src/riscv-isa-sim/issues/1493
    return ['script', '-c', f'spike --isa=RV32GC {bench}', '-e']


def decode_results(stdout_str, stderr_str):
    """Extract the results from the output string of the run. Return the
       elapsed time in milliseconds or zero if the run failed."""
    # See above in build_benchmark_cmd how we record the return value and
    # execution time.

    time = re.search('Spike mcycle timer delta: (\d+)', stdout_str, re.S)
    fake_freq = 1e6 # 1 MHz
    fake_period = 1.0 / fake_freq

    if time:
        s_elapsed = int(time.group(1)) * fake_period
        ms_elapsed = s_elapsed * 1000
        # Return value cannot be zero (will be interpreted as error)
        return max(float(ms_elapsed), 0.001)

    # We must have failed to find a time
    log.debug('Warning: Failed to find timing')
    return 0.0
