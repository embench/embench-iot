#!/usr/bin/env python3

# Script to build and run all benchmarks

# Copyright (C) 2017, 2019 Embecosm Limited
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Run sets of Embench benchmarks
"""


import argparse
import os
import shutil
import subprocess
import sys

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

# The various sets of benchmarks we could run

rv32_gcc_opt_runset = {
    'name' : 'RV32IMC GCC optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'speed benchmark' : {
        'timeout' : 1800,
        'arglist' : [
            './benchmark_speed.py',
            '--target-module=run_gdbserver_sim',
	    '--gdbserver-command=riscv32-gdbserver',
	    '--gdb-command=riscv32-unknown-elf-gdb',
            '--json-output',
        ],
        'desc' : 'run'
    },
    'runs' : [
        { 'name' : 'rv32imc-opt-os-save-restore',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
        },
        { 'name' : 'rv32imc-opt-os',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os',
        },
        { 'name' : 'rv32imc-opt-o0',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O0',
        },
        { 'name' : 'rv32imc-opt-o1',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O1',
        },
        { 'name' : 'rv32imc-opt-o2',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
        },
        { 'name' : 'rv32imc-opt-o3',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3',
        },
        { 'name' : 'rv32imc-opt-o3-inline-40',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3 -finline-functions ' +
                     '-finline-limit=40',
        },
        { 'name' : 'rv32imc-opt-o3-unroll-inline-200',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3 -funroll-all-loops ' +
                     '-finline-functions -finline-limit=200',
        },
    ]
}

rv32_gcc_isa_runset = {
    'name' : 'RV32 GCC ISA comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'speed benchmark' : {
        'timeout' : 1800,
        'arglist' : [
            './benchmark_speed.py',
            '--target-module=run_gdbserver_sim',
	    '--gdbserver-command=riscv32-gdbserver',
	    '--gdb-command=riscv32-unknown-elf-gdb',
            '--json-output',
        ],
        'desc' : 'run'
    },
    'runs' : [
        { 'name' : 'rv32i-isa-os-save-restore',
          'cflags' : '-march=rv32i -mabi=ilp32 -Os -msave-restore',
        },
        { 'name' : 'rv32im-isa-os-save-restore',
          'cflags' : '-march=rv32im -mabi=ilp32 -Os -msave-restore',
        },
        { 'name' : 'rv32imc-isa-os-save-restore',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
        },
        { 'name' : 'rv32i-isa-o2',
          'cflags' : '-march=rv32i -mabi=ilp32 -O2',
        },
        { 'name' : 'rv32im-isa-o2',
          'cflags' : '-march=rv32im -mabi=ilp32 -O2',
        },
        { 'name' : 'rv32imc-isa-o2',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
        },
    ]
}


def build_parser():
    """Build a parser for all the arguments"""
    parser = argparse.ArgumentParser(description='Build all the benchmarks')

    parser.add_argument(
        '--resdir',
        type=str,
        default='results',
        help='Directory in which to place results files',
    )
    parser.add_argument(
        '--rv32-gcc-opt',
        action='store_true',
        help='Run RISC-V GCC optimization comparison benchmarks'
    )
    parser.add_argument(
        '--rv32-gcc-isa',
        action='store_true',
        help='Run RISC-V GCC isa comparison benchmarks'
    )

    return parser


def build_benchmarks(arch, chip, board, cc='cc', cflags=None, ldflags=None,
                     dummy_libs=None, user_libs=None):
    """Build all the benchmarks"""

    # Construct the argument list
    arglist = [
        f'./build_all.py',
        f'--clean',
        f'--arch={arch}',
        f'--chip={chip}',
	f'--board={board}',
        f'--cc={cc}',
    ]
    if cflags:
        arglist.append(f'--cflags={cflags}')
    if ldflags:
        arglist.append(f'--ldflags={ldflags}')
    if dummy_libs:
        arglist.append(f'--dummy-libs={dummy_libs}')
    if user_libs:
        arglist.append(f'--user-libs={user_libs}')

    # Run the build script
    try:
        res = subprocess.run(
            arglist,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        if res.returncode == 0:
            if not ('All benchmarks built successfully' in
                    res.stdout.decode('utf-8')):
                print('ERROR: Not all benchmarks built successfully')
                sys.exit(1)
        else:
            print(f'ERROR: {arglist} failed')
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f'ERROR: {arglist} timed out')
        sys.exit(1)


def benchmark(arglist, timeout, desc, resfile, append):
    """Run the speed benchmark script"""

    # Run the benchmark script
    try:
        res = subprocess.run(
            arglist,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        if res.returncode == 0:
            if not ('All benchmarks ' + desc +' successfully' in
                    res.stdout.decode('utf-8')):
                print('ERROR: Not all benchmarks ' + desc + ' successfully')
                sys.exit(1)
        else:
            print(f'ERROR: {arglist} failed')
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f'ERROR: {arglist} timed out')
        sys.exit(1)

    # Dump the data
    with open(resfile, 'a') as fileh:
        for line in res.stdout.decode('utf-8').splitlines(keepends=True):
            if not 'All benchmarks ' + desc + ' successfully' in line:
                fileh.writelines(line)
        fileh.close()


def main():
    """Main program to drive building of benchmarks."""

    # Parse arguments using standard technology
    parser = build_parser()
    args = parser.parse_args()

    runsets = []

    if args.rv32_gcc_opt:
        runsets.append(rv32_gcc_opt_runset)
    if args.rv32_gcc_isa:
        runsets.append(rv32_gcc_isa_runset)

    if not runsets:
        print("ERROR: No run sets specified")
        sys.exit(1)

    # Take each runset in turn
    for rs in runsets:
        print(rs['name'])

        for r in rs['runs']:
            name = r['name']
            cflags = r['cflags']
            print(f'  {name}')
            resfile = os.path.join('results', name + '.json')

            # Size benchmark
            build_benchmarks(
                arch='riscv32',
                chip='generic',
	        board='ri5cyverilator',
            cc='riscv32-unknown-elf-gcc',
                cflags=f'{cflags}',
                ldflags='-nostartfiles -nostdlib',
                dummy_libs='crt0 libc libgcc libm'
            )
            benchmark(
                arglist=rs['size benchmark']['arglist'],
                timeout=rs['size benchmark']['timeout'],
                desc=rs['size benchmark']['desc'],
                resfile=resfile,
                append=False
            )

            # Speed benchmark
            build_benchmarks(
                arch='riscv32',
                chip='generic',
	        board='ri5cyverilator',
                cc='riscv32-unknown-elf-gcc',
                cflags=f'{cflags}',
                user_libs='-lm'
            )
            benchmark(
                arglist=rs['speed benchmark']['arglist'],
                timeout=rs['speed benchmark']['timeout'],
                desc=rs['speed benchmark']['desc'],
                resfile=resfile,
                append=True
            )


# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
