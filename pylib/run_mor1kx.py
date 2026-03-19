#!/usr/bin/env python3

"""
Target runner for OpenRISC benchmarks via FuseSoC.

This module is loaded by benchmark_speed.py and provides:
- target-specific CLI argument parsing
- command construction for FuseSoC simulation runs
- result decoding from simulator output
"""

__all__ = [
    'get_target_args',
    'build_benchmark_cmd',
    'decode_results',
    'run_benchmark',
]

import argparse
import subprocess
import re
import os

from embench_core import log

cpu_mhz = 1

# Default config path computed relative to this file
_DEFAULT_CONFIG = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 
                 '..', 'examples', 'openrisc', 'fusesoc.conf')
)

def get_target_args(remnant):
    """Parse target-specific command-line arguments."""
    parser = argparse.ArgumentParser(description='Get target specific args')


    parser.add_argument(
        '--config-path',
        type=str,
        default=_DEFAULT_CONFIG,
        help='path to fusesoc.conf.'
    )

    parser.add_argument(
        '--target',
        type=str,
        default='mor1kx_tb',
        help='target to test'
    )

    parser.add_argument(
        '--tool',
        type=str,
        default='verilator',
        help='tool to use (verilator highly recommended)'
    )

    parser.add_argument(
        '--system',
        type=str,
        default='::mor1kx-generic:1.1',
        help='soc to test'
    )

    parser.add_argument(
        '--fusesoc_target',
        type=str,
        default='mor1kx_tb',
        help='soc to test'
    )

    parser.add_argument(
        '--ext_args',
        type=str,
        default='',
        help='extra args to pass after all other arguments (i.e. to turn on tracing)'
    )

    return parser.parse_args(remnant)


def build_benchmark_cmd(path, args):
    """Build the FuseSoC command used to run one benchmark executable."""

    out = [
        'fusesoc', '--config', args.config_path, 'run', '--target',
        args.fusesoc_target, '--tool', args.tool, args.system, '--elf_load',
        path
    ]

    return out


def decode_results(stdout_str, stderr_str):
    """Decode simulator output and return elapsed time in milliseconds.

    Returns 0.0 when the run does not indicate successful completion or when
    timing data cannot be found.
    """

    global cpu_mhz
    
    combined_output = stdout_str + stderr_str
    
    log.info(stdout_str)
    rcstr = re.search(r'Success! Got NOP_EXIT', combined_output, re.S)
    if not rcstr:
        log.debug('Warning: Failed to find return code')
        return 0.0

    time = re.search(r'End time\s+([0-9A-Fa-fx]+)', combined_output, re.S)
    if time:
        time_value = time.group(1)
        base = 16 if re.search(r'[A-Fa-fx]', time_value) else 10
        ms_elapsed = int(time_value, base) / cpu_mhz / 1000.0
        return max(float(ms_elapsed), 0.001)

    exit_cycles = re.search(r'NOP_EXIT\. Exiting \(([0-9A-Fa-fx]+)\)',
                            combined_output, re.S)
    if exit_cycles:
        cycle_value = exit_cycles.group(1)
        base = 16 if re.search(r'[A-Fa-fx]', cycle_value) else 10
        ms_elapsed = int(cycle_value, base) / cpu_mhz / 1000.0
        return max(float(ms_elapsed), 0.001)

    log.debug('Warning: Failed to find timing')
    return 0.0


def run_benchmark(bench, path, args):
    """Run one benchmark executable and return elapsed time in milliseconds.

    Returns None when the process times out or exits with a non-zero code.
    """
    global cpu_mhz
    cpu_mhz = args.cpu_mhz

    arglist = build_benchmark_cmd(path, args)
    try:
        res = subprocess.run(
            arglist,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired:
        log.warning(f'Warning: Run of {bench} timed out.')
        return None

    if res.returncode != 0:
        log.warning(f'Warning: Run of {bench} failed with return code {res.returncode}.')
        stdout_tail = res.stdout.decode('utf-8', errors='replace')[-800:]
        stderr_tail = res.stderr.decode('utf-8', errors='replace')[-800:]
        if stderr_tail.strip():
            log.warning(f'Warning: stderr tail for {bench}:\n{stderr_tail}')
        elif stdout_tail.strip():
            log.warning(f'Warning: stdout tail for {bench}:\n{stdout_tail}')
        return None

    return decode_results(res.stdout.decode('utf-8'), res.stderr.decode('utf-8'))