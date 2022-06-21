#!/usr/bin/env python3

# Python module to open and decode results from Wally.

# Copyright (C) 2022 Embecosm Limited and University of Bristol
#
# Contributor: Daniel Torres <dtorres@hmc.edu>
#
# This file is part of Embench.


"""
Embench module to run benchmark programs.

This version is suitable for running programs on wally.
"""

__all__ = [
    'get_target_args',
    'build_benchmark_cmd',
    'decode_results',
]

import argparse
import configparser
import re

from embench_core import log

cpu_mhz = 1

def get_target_args(remnant):
    """Parse left over arguments"""
    parser = argparse.ArgumentParser(description='Get target specific args')

    # No target arguments
    parser.add_argument(
        '--cpu-mhz',
        type=int,
        default=1,
        help='Processor clock speed in MHz'
    )

    return parser.parse_args(remnant)


def build_benchmark_cmd(bench, args):
    """Construct the command to run the benchmark.  "args" is a
       namespace with target specific arguments"""
    global cpu_mhz
    cpu_mhz = args.cpu_mhz
    # to run wally, we use the modelsim that inputs the compiled C code and outputs a .outputfile
    # that contains the content of begin_signature, which writes the instret & cycles of begin & end triggers
    # along with the return code, which tells us if the test passed
    log.debug("\"" + bench + "\" : cycles, insret, CPI, Elapsed Time, ClkFreq")
    return ['sh', '-c', ('cat *.output')]

def decode_results(stdout_str, stderr_str):
    """Extract the results from the output string of the run. Return the
       elapsed time in milliseconds or zero if the run failed."""
    # this reads in the output of the buildbench_cmd command, in this case we have 5 lines written to stdout_str
    # that contains the content of begin_signature, which writes the instret & cycles of begin & end triggers
    # along with the return code, which tells us if the test passed
    output_signature = stdout_str.split('\n')[0:6]
    if (len(output_signature)):
        pc_trigger = list(map(lambda s: int(s,16), output_signature[0:5]))
    else:
        log.debug('Warning: Output file empty')
        result = 0.0
    
    # get the cpu_mhz from input variable of benchmark_speed.py
    global cpu_mhz
    # check if either pc value is the default (i.e. never got written to)
    if (pc_trigger[4]!=1):
        log.debug('Warning: Simulation returned failure in signature')
    if ((pc_trigger[1]==0)|(pc_trigger[0]==0)):
        log.debug('Warning: Failed to find timing')
        result = 0.0
    else:
        result = ((pc_trigger)[1]-(pc_trigger)[0]) / cpu_mhz / 1000.0

    # log.debug('Simulation returned %d. 1 is Success, 3 is Failure', pc_trigger[4])
    # cycles, #insret, #CPI, Elapsed Time, ClkFreq
    log.debug( "[" + str((pc_trigger)[1]-(pc_trigger)[0]) + "," +  str(pc_trigger[3]-pc_trigger[2]) + "," + str((pc_trigger[1]-pc_trigger[0]) / (pc_trigger[3]-pc_trigger[2])) + "," + str(result) + "," + str(cpu_mhz) + "],") 

    return (result)