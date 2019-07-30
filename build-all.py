#!/usr/bin/env python3

# Script to build all benchmarks

# Copyright (C) 2017, 2019 Embecosm Limited
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
import traceback

# Handle for the logger
log = logging.getLogger()

# All the global parameters
gp = dict()

# All the benchmarks
benchmarks = []

def build_parser():
    """Build a parser for all the arguments"""
    parser = argparse.ArgumentParser(
        description='Build all the benchmarks')

    parser.add_argument(
        '--arch', type=str, required=True,
        help='The architecture for which to build'
    )
    parser.add_argument(
        '--chip', type=str, default='default',
        help='The chip for which to build'
    )
    parser.add_argument(
        '--board', type=str, default='default',
        help='The board for which to build'
    )
    parser.add_argument(
        '--cc', type=str, default='cc', help='C compiler to use'
    )
    parser.add_argument(
        '--ld', type=str, help='Linker to use'
    )
    parser.add_argument(
        '--user-cppflags', type=str,
                        help='Additional C pre-processor flags to use'
    )
    parser.add_argument(
        '--user-cflags', type=str, help='Additional C compiler flags to use'
    )
    parser.add_argument(
        '--user-ldflags', type=str,
                        help='Additional linker flags to use'
    )
    parser.add_argument(
        '--user-libs', type=str, help='Additional libraries to use'
    )

    # Note that we don't use store_true, since if the argument is not
    # specified, we do not want a value specified.
    parser.add_argument(
        '--use-dummy-crt0', action='store_const', const=True,
        help='Use dummy C runtime startup'
    )
    parser.add_argument(
        '--use-dummy-libc', action='store_const', const=True,
        help='Use dummy standard C library'
    )
    parser.add_argument(
        '--use-dummy-libgcc', action='store_const', const=True,
        help='Use dummy GCC emulation library'
    )
    parser.add_argument(
        '--use-dummy-compilerrt', action='store_const', const=True,
        help='Use dummy LLVM emulation library'
    )
    parser.add_argument(
        '--use-dummy-libm', action='store_const', const=True,
        help='Use dummy standard C math library'
    )
    parser.add_argument(
        '--clean', action='store_true', help='Rebuild everything'
    )
    parser.add_argument(
        '--builddir', type=str, default='bd',
        help='Directory in which to build'
    )
    parser.add_argument(
        '--logdir', type=str, default='logs',
        help='Directory in which to store logs',
    )
    parser.add_argument(
        '--warmup-heat', type=int, default='1',
        help='Number of warmup loops to execute before benchmark'
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
    log.debug(f'Architecture:         {args.arch}')
    log.debug(f'Chip:                 {args.chip}')
    log.debug(f'Board:                {args.board}')
    log.debug(f'C compiler:           {args.cc}')
    log.debug(f'Linker:               {args.ld}')
    if args.user_cppflags:
        log.debug(f'User CPPFLAGS:        {args.user_cppflags}')
    if args.user_cflags:
        log.debug(f'User CFLAGS:          {args.user_cflags}')
    if args.user_ldflags:
        log.debug(f'User LDFLAGS:         {args.user_ldflags}')
    if args.user_libs:
        log.debug(f'User libraries:       {args.user_libs}')
    if args.use_dummy_crt0:
        log.debug(f'Use dummy CRT0:       {args.use_dummy_crt0}')
    if args.use_dummy_libc:
        log.debug(f'Use dummy libc:       {args.use_dummy_libc}')
    if args.use_dummy_libgcc:
        log.debug(f'Use dummy libgcc:     {args.use_dummy_libgcc}')
    if args.use_dummy_compilerrt:
        log.debug(f'Use dummy CompilerRT: {args.use_dummy_compilerrt}')
    if args.use_dummy_libm:
        log.debug(f'Use dummy libm:       {args.use_dummy_libm}')
    log.debug(f'Build directory:      {args.builddir}')
    log.debug(f'Log directory:        {args.logdir}')
    log.debug('')


def validate_args(args):
    """Check that supplied args are all valid. By definition logging is
       working when we get here. Don't bother with build directory, since
       that will be checked when we create it.

       Update the gp dictionary with all the useful info"""
    gp['configdir']    = os.path.join(gp['rootdir'], 'config')
    gp['bd_configdir'] = os.path.join(gp['bd'], 'config')
    good_args = True

    # Architecture
    if len(args.arch) == 0:
        log.error('ERROR: Null achitecture not permitted: exiting')
        sys.exit(1)

    gp['archdir']    = os.path.join(gp['configdir'], args.arch)
    gp['bd_archdir'] = os.path.join(gp['bd_configdir'], args.arch)
    if not os.path.isdir(gp['archdir']):
        log.error(f'ERROR: Architecture "{args.arch}" not found: exiting')
        sys.exit(1)
    if not os.access(gp['archdir'], os.R_OK):
        log.error(f'ERROR: Unable to read achitecture "{args.arch}": exiting')
        sys.exit(1)

    # Chip
    if len(args.chip) == 0:
        log.error('ERROR: Null chip not permitted: exiting')

    gp['chipdir']    = os.path.join(gp['archdir'], 'chips', args.chip)
    gp['bd_chipdir'] = os.path.join(gp['bd_archdir'], 'chips', args.chip)
    if not os.path.isdir(gp['chipdir']):
        log.error(
            f'ERROR: Chip "{args.chip}" not found for architecture ' +
            f'"{args.arch}: exiting'
        )
        sys.exit(1)
    if not os.access(gp['chipdir'], os.R_OK):
        log.error(
            f'ERROR: Unable to read chip "{args.chip}" for architecture ' +
            f'"{args.arch}": exiting'
        )
        sys.exit(1)

    # Board
    if len(args.board) == 0:
        log.error('ERROR: Null board not permitted: exiting')

    gp['boarddir']    = os.path.join(gp['archdir'], 'boards', args.board)
    gp['bd_boarddir'] = os.path.join(gp['bd_archdir'], 'boards', args.board)
    if not os.path.isdir(gp['boarddir']):
        log.error(f'ERROR: Board "{args.board}" not found for architecture ' +
               f'"{args.arch}: exiting')
        sys.exit(1)
    if not os.access(gp['boarddir'], os.R_OK):
        log.error(
            f'ERROR: Unable to read board "{args.board}" for architecture ' +
            f'"{args.arch}": exiting'
        )
        sys.exit(1)

    # C compiler
    if shutil.which(args.cc):
        gp['cc'] = args.cc
    else:
        log.error(f'ERROR: Compiler {args.cc} not found on path: exiting')
        sys.exit(1)

    # Linker - if not specified defaults to C compiler
    if args.ld:
        gp['ld'] = args.ld
    else:
        gp['ld'] = args.cc

    if not shutil.which(gp['ld']):
        log.error(f'ERROR: Linker {gp["ld"]} not found on path: exiting')
        sys.exit(1)

    # Flags are always OK


def create_builddir(builddir, clean):
    """Create the build directory, which can be relative to the current
       directory or absolute. If the "clean" is True, delete any existing
       build directory"""
    if os.path.isabs(builddir):
        gp['bd'] = builddir
    else:
        gp['bd'] = os.path.join(gp['rootdir'], builddir)

    if (os.path.isdir(gp['bd']) and clean):
        try:
            shutil.rmtree(gp['bd'])
        except:
            log.error(
                f'ERROR: Unable to clean build directory "{gp["bd"]}: ' +
                'exiting'
            )

    if not os.path.isdir(gp['bd']):
        try:
            os.makedirs(gp['bd'])
        except PermissionError as e:
            raise PermissionError(
                f'Unable to create build directory {gp["bd"]}'
            )

    if not os.access(gp['bd'], os.W_OK):
        raise PermissionError(
            f'Unable to write to build directory {gp["bd"]}'
        )


def find_benchmarks():
    """Enumerate all the benchmarks in alphabetical order into the global
       variable, 'benchmarks'. The benchmarks are found in the 'src'
       subdirectory of the benchmarks repo."""
    gp['benchdir']    = os.path.join(gp['rootdir'], 'src')
    gp['bd_benchdir'] = os.path.join(gp['bd'], 'src')
    dirlist = os.listdir(gp['benchdir'])

    benchmarks.clear()

    for b in dirlist:
        abs_b = os.path.join (gp['benchdir'], b)
        if os.path.isdir(abs_b):
            benchmarks.append(b)

    benchmarks.sort()


def log_benchmarks():
    """Record all the benchmarks in the log"""
    log.debug('Benchmarks')
    log.debug('==========')

    for b in benchmarks:
        log.debug(b)

    log.debug('')


def set_parameters(args):
    """Determine all remaining parameters"""
    gp['supportdir']    = os.path.join(gp['rootdir'], 'support')
    gp['bd_supportdir'] = os.path.join(gp['bd'], 'support')

    gp['cppflags']             = [
        f'-I{gp["supportdir"]}', f'-I{gp["boarddir"]}', f'-I{gp["chipdir"]}',
        f'-I{gp["archdir"]}', f'-DWARMUP_HEAT={args.warmup_heat}'
    ]
    gp['cflags']               = []
    gp['ldflags']              = []
    gp['libs']                 = []
    gp['use_dummy_crt0']       = False
    gp['use_dummy_libc']       = False
    gp['use_dummy_libgcc']     = False
    gp['use_dummy_compilerrt'] = False
    gp['use_dummy_libm']       = False

    # Architecture specific flags may be defined in a file which may create the
    # dictionary arch_config. We define an empty dictionary in case it is not
    # set. These flags take priority over the internal flags, since they are
    # later in the sequence.
    arch_config = {}
    arch_conf_file = os.path.join(gp['archdir'], 'arch.cfg')
    if os.path.isfile(arch_conf_file):
        with open(arch_conf_file) as f:
            try:
                exec(f.read())
            except:
                log.error(
                    'ERROR: Corrupt architecture config file ' +
                    f'{arch_conf_file}: exiting'
                    )
                sys.exit(1)

        # Parse the configuration
        if 'arch_cppflags' in arch_config:
            gp['cppflags'].extend(arch_config['arch_cppflags'])
        if 'arch_cflags' in arch_config:
            gp['cflags'].extend(arch_config['arch_cflags'])
        if 'arch_ldflags' in arch_config:
            gp['ldflags'].extend(arch_config['arch_ldflags'])
        if 'arch_libs' in arch_config:
            gp['libs'].extend(arch_config['arch_libs'])

        if 'use_dummy_crt0' in arch_config:
            gp['use_dummy_crt0'] = arch_config['use_dummy_crt0']
        if 'use_dummy_libc' in arch_config:
            gp['use_dummy_libc'] = arch_config['use_dummy_libc']
        if 'use_dummy_libgcc' in arch_config:
            gp['use_dummy_libgcc'] = arch_config['use_dummy_libgcc']
        if 'use_dummy_compilerrt' in arch_config:
            gp['use_dummy_compilerrt'] = arch_config['use_dummy_compilerrt']
        if 'use_dummy_libm' in arch_config:
            gp['use_dummy_libm'] = arch_config['use_dummy_libm']

    # Check if architecture support file exists
    arch_header = os.path.join(gp['archdir'], 'archsupport.h')
    if os.path.isfile(arch_header):
        gp['cppflags'].append('-DHAVE_ARCHSUPPORT_H')

    # Chip specific flags may be defined in a file which may create the
    # dictionary chip_config. We define an empty dictionary in case it is not
    # set. These flags tkae priority over the internal and architecture
    # specific flags, since they are later in the sequence.
    chip_config = {}
    chip_conf_file = os.path.join(gp['chipdir'], 'chip.cfg')
    if os.path.isfile(chip_conf_file):
        with open(chip_conf_file) as f:
            try:
                exec(f.read())
            except:
                log.error(
                    'ERROR: Corrupt chip config file ' +
                    f'{chip_conf_file}: exiting'
                    )
                sys.exit(1)

        # Parse the configuration
        if 'chip_cppflags' in chip_config:
            gp['cppflags'].extend(chip_config['chip_cppflags'])
        if 'chip_cflags' in chip_config:
            gp['cflags'].extend(chip_config['chip_cflags'])
        if 'chip_ldflags' in chip_config:
            gp['ldflags'].extend(chip_config['chip_ldflags'])
        if 'chip_libs' in chip_config:
            gp['libs'].extend(chip_config['chip_libs'])

        if 'use_dummy_crt0' in chip_config:
            gp['use_dummy_crt0'] = chip_config['use_dummy_crt0']
        if 'use_dummy_libc' in chip_config:
            gp['use_dummy_libc'] = chip_config['use_dummy_libc']
        if 'use_dummy_libgcc' in chip_config:
            gp['use_dummy_libgcc'] = chip_config['use_dummy_libgcc']
        if 'use_dummy_compilerrt' in chip_config:
            gp['use_dummy_compilerrt'] = chip_config['use_dummy_compilerrt']
        if 'use_dummy_libm' in chip_config:
            gp['use_dummy_libm'] = chip_config['use_dummy_libm']

    # Check if chip support file exists
    chip_header = os.path.join(gp['chipdir'], 'chipsupport.h')
    if os.path.isfile(chip_header):
        gp['cppflags'].append('-DHAVE_CHIPSUPPORT_H')

    # Board specific flags may be defined in a file which may create the
    # dictionary board_config. We define an empty dictionary in case it is not
    # set. These flags tkae priority over the internal, architecture and chip
    # specific flags, since they are later in the sequence.
    board_config = {}
    board_conf_file = os.path.join(gp['boarddir'], 'board.cfg')
    if os.path.isfile(board_conf_file):
        with open(board_conf_file) as f:
            try:
                exec(f.read())
            except:
                log.error(
                    'ERROR: Corrupt board config file ' +
                    f'{board_conf_file}: exiting'
                    )
                sys.exit(1)

        # Parse the configuration
        if 'board_cppflags' in board_config:
            gp['cppflags'].extend(board_config['board_cppflags'])
        if 'board_cflags' in board_config:
            gp['cflags'].extend(board_config['board_cflags'])
        if 'board_ldflags' in board_config:
            gp['ldflags'].extend(board_config['board_ldflags'])
        if 'board_libs' in board_config:
            gp['libs'].extend(board_config['board_libs'])

        if 'use_dummy_crt0' in board_config:
            gp['use_dummy_crt0'] = board_config['use_dummy_crt0']
        if 'use_dummy_libc' in board_config:
            gp['use_dummy_libc'] = board_config['use_dummy_libc']
        if 'use_dummy_libgcc' in board_config:
            gp['use_dummy_libgcc'] = board_config['use_dummy_libgcc']
        if 'use_dummy_compilerrt' in board_config:
            gp['use_dummy_compilerrt'] = board_config['use_dummy_compilerrt']
        if 'use_dummy_libm' in board_config:
            gp['use_dummy_libm'] = board_config['use_dummy_libm']

    # Check if board support file exists
    board_header = os.path.join(gp['boarddir'], 'boardsupport.h')
    if os.path.isfile(board_header):
        gp['cppflags'].append('-DHAVE_BOARDSUPPORT_H')

    # User specified flags are defined on the command line. These are placed
    # last in the command line, so take priority over all other flags.

    # Parse the arguments
    if args.user_cppflags:
        gp['cppflags'].extend(args.user_cppflags.split(sep=' '))
    if args.user_cflags:
        gp['cflags'].extend(args.user_cflags.split(sep=' '))
    if args.user_ldflags:
        gp['ldflags'].extend(args.user_ldflags.split(sep=' '))
    if args.user_libs:
        gp['libs'].extend(args.user_libs.split(sep=' '))

    if args.use_dummy_crt0:
        gp['use_dummy_crt0'] = True
    if args.use_dummy_libc:
        gp['use_dummy_libc'] = True
    if args.use_dummy_libgcc:
        gp['use_dummy_libgcc'] = True
    if args.use_dummy_compilerrt:
        gp['use_dummy_compilerrt'] = True
    if args.use_dummy_libm:
        gp['use_dummy_libm'] = True


def log_parameters():
    """Record all the global parameters in the log"""
    log.debug('Global parameters')
    log.debug('=================')

    for k, v in gp.items():
        log.debug(f'{k:<21}: {v}')

    log.debug('')


def compile_file(f_root, srcdir, bindir):
    """Compile a single C file, with the given file root, "f_root", from the
       source directory, "srcdir", in to the bin directory, "bindir" using the
       general preprocessor and C compilation flags.

       Return True if the compilation success, False if it fails. Log
       everything in the event of failure"""
    abs_src = os.path.join(f'{srcdir}', f'{f_root}.c')
    abs_bin = os.path.join(f'{bindir}', f'{f_root}.o')

    # Construct the argument list
    arglist = [f'{gp["cc"]}', '-c']
    arglist.extend(gp['cppflags'])
    arglist.extend(gp['cflags'])
    arglist.extend(['-o', f'{f_root}.o', abs_src])

    # Run the compilation, but only if the source file is newer than the
    # binary.
    succeeded = True

    if (not os.path.isfile(abs_bin) or
        (os.path.getmtime(abs_src) > os.path.getmtime(abs_bin))):
        try:
            res = subprocess.run(
                arglist,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=bindir,
                timeout=5
            )
        except TimeoutExpired:
            log.warning(
                f'Warning: Compilation of {f_root}.c from source directory ' +
                f'{srcdir} to binary directory {bindir} timed out'
            )
            succeeded = False
            pass

        if 0 != res.returncode:
            log.warning(
                f'Warning: Compilation of {f_root}.c from source directory ' +
                f'{srcdir} to binary directory {bindir} failed'
            )
            succeeded = False

    if not succeeded:
        log.debug('Args to subprocess:')
        log.debug(f'{arglist}')
        log.debug(res.stdout.decode('utf-8'))
        log.debug(res.stderr.decode('utf-8'))

    return succeeded


def compile_benchmark(b):
    """Compile the benchmark, "b".

       Return True if all files compile successfully, False otherwise."""
    abs_src_b = os.path.join(gp['benchdir'], b)
    abs_bd_b  = os.path.join (gp['bd_benchdir'], b)
    succeeded = True

    if not os.path.isdir(abs_bd_b):
        try:
            os.makedirs(abs_bd_b)
        except:
            log.warning('Warning: Unable to create build directory for ' +
                        f'benchmark {b}')
            return False

    # Compile each file in the benchmark
    for f in os.listdir(abs_src_b):
        f_root, ext = os.path.splitext(f)
        if ext == '.c':
            succeeded &= compile_file(f_root, abs_src_b, abs_bd_b)

    return succeeded


def compile_support():
    """Compile all the support code.

       Return True if all files compile successfully, False otherwise."""
    succeeded = True

    # First the general support
    if not os.path.isdir(gp['bd_supportdir']):
        try:
            os.makedirs(gp['bd_supportdir'])
        except:
            log.warning('Warning: Unable to create support build directory ' +
                        f'{gp["bd_supportdir"]}')
            return False

    # Compile each general support file in the benchmark
    succeeded &= compile_file('beebsc', gp['supportdir'], gp['bd_supportdir'])
    succeeded &= compile_file('main', gp['supportdir'], gp['bd_supportdir'])

    # Compile dummy files that are needed
    for d in {'crt0', 'libc', 'libgcc', 'compilerrt', 'libm'}:
        if gp['use_dummy_' + d]:
            succeeded &= compile_file(
                'dummy-' + d, gp['supportdir'], gp['bd_supportdir']
            )

    # Compile architecture, chip and board specific files.  Note that we only
    # create the build directory if it is needed here.
    for d in {'arch', 'chip', 'board'}:
        f = os.path.join(gp[d + 'dir'], d + 'support.c')
        if os.path.isfile(f):
            # Create build directory
            bd = gp['bd_' + d + 'dir']
            if not os.path.isdir(bd):
                try:
                    os.makedirs(bd)
                except:
                    log.warning('Warning: Unable to create build directory ' +
                                f'for {d}, "{bd}')
                    return False

            succeeded &= compile_file(
                d + 'support', gp[d + 'dir'], gp['bd_' + d + 'dir']
            )

    return succeeded


def link_benchmark(b):
    """Link the benchmark, "b".

       Return True if link is successful, False otherwise."""
    abs_bd_b  = os.path.join (gp['bd_benchdir'], b)
    succeeded = True

    if not os.path.isdir(abs_bd_b):
        log.warning('Warning: Unable to find build directory for ' +
                        f'benchmark {b}')
        return False

    # Build up a list of files to include in the binary. They are all
    # absolute, apart from those in the benchmark, since we will link in its
    # build directory.
    binlist = []
    for f in os.listdir(abs_bd_b):
        if f.endswith('.o'):
            binlist.append(f)

    # Add arch, chip and board binaries
    for d in {'arch', 'chip', 'board'}:
        f = os.path.join(gp[f'bd_{d}dir'], f'{d}support.o')
        if os.path.isfile(f):
            binlist.append(f)

    # Add generic support
    for d in {'main', 'beebsc'}:
        f = os.path.join(gp['bd_supportdir'], f'{d}.o')
        if os.path.isfile(f):
            binlist.append(f)
        else:
            succeeded = False
            log.warning(f'Warning: Unable to find support library {f}')

    # Add dummy binaries
    for d in {'crt0', 'libc', 'libgcc', 'compilerrt', 'libm'}:
        if gp['use_dummy_' + d]:
            f = os.path.join(gp['bd_supportdir'], f'dummy-{d}.o')
            if os.path.isfile(f):
                binlist.append(f)
            else:
                succeeded = False
                log.warning(f'Warning: Unable to find dummy library {f}')

    # Construct the argument list
    arglist = [f'{gp["ld"]}']
    arglist.extend(gp['ldflags'])
    arglist.extend(['-o', b])
    arglist.extend(binlist)
    arglist.extend(gp['libs'])

    # Run the link
    try:
        res = subprocess.run(
            arglist,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=abs_bd_b,
            timeout=5
        )
    except TimeoutExpired:
        log.warning(f'Warning: link of benchmark "{b}" timed out')
        succeeded = False
        pass

    if 0 != res.returncode:
        log.warning(f'Warning: Link of benchmark "{b}" failed')
        succeeded = False

    if not succeeded:
        log.debug('Args to subprocess:')
        log.debug(f'{arglist}')
        log.debug(res.stdout.decode('utf-8'))
        log.debug(res.stderr.decode('utf-8'))

    return succeeded


def main():
    # Establish the root directory of the repository, since we know this file is
    # in that directory.
    gp['rootdir'] = os.path.abspath(os.path.dirname(__file__))

    # Parse arguments using standard technology
    parser = build_parser()
    args   = parser.parse_args()

    # Establish logging
    logdir  = create_logdir(args.logdir)
    logfile = os.path.join(logdir, time.strftime('build-%Y-%m-%d-%H%M%S.log'))
    setup_logging(logfile)
    log_args(args)
    log.debug(f'Log file:        {logfile}\n')

    # Establish build directory
    builddir = create_builddir(args.builddir, args.clean)

    # Check args are OK (have to have logging and build directory set up first)
    validate_args(args)

    # Find the benchmarks
    find_benchmarks()
    log_benchmarks()

    # Establish other global parameters
    set_parameters(args)
    log_parameters()

    log.debug('General log')
    log.debug('===========')

    # Track success
    successful = compile_support()
    if successful:
        log.debug(f'Compilation of support files successful')


    for b in benchmarks:
        res = compile_benchmark(b)
        successful &=res
        if res:
            log.debug(f'Compilation of benchmark "{b}" successful')
            res = link_benchmark(b)
            successful &=res
            if res:
                log.debug(f'Linking of benchmark "{b}" successful')
                log.info(f'{b}')

    if successful:
        log.info('All benchmarks built successfully')

# Only run if this is the main package

if __name__ == '__main__':
    sys.exit(main())
