# Chip configuration for Baseline RISC-V Configuration
#
# Copyright (C) 2019 Embecosm Limited and the University of Bristol
#
# Contributor Graham Markall <graham.markall@embecosm.com>
# Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>
# Contributor Ola Jeppsson   <ola.jeppsson@gmail.com>
#
# This file is part of Embench.
#
# SPDX-License-Identifier: GPL-3.0-or-later

# This is a python setting of parameters for the chip.  The following
# parameters may be set (other keys are silently ignored).  Defaults are shown
# in brackets
# - cc ('cc')
# - ld (same value as for cc)
# - cflags ([])
# - ldflags ([])
# - cc_define_pattern ('-D{0}')
# - cc_incdir_pattern ('-I{0}')
# - cc_input_pattern ('{0}')
# - cc_output_pattern ('-o {0}')
# - ld_input_pattern ('{0}')
# - ld_output_pattern ('-o {0}')
# - user_libs ([])
# - dummy_libs ([])
# - cpu_mhz (1)
# - warmup_heat (1)

# The "flags" and "libs" parameters (cflags, ldflags, user_libs, dummy_libs)
# should be lists of arguments to be passed to the compile or link line as
# appropriate.  Patterns are Python format patterns used to create arguments.
# Thus for GCC or Clang/LLVM defined constants can be passed using the prefix
# '-D', and the pattern '-D{0}' would be appropriate (which happens to be the
# default).

# "user_libs" may be absolute file names or arguments to the linker. In the
# latter case corresponding arguments in ldflags may be needed.  For example
# with GCC or Clang/LLVM is "-l" flags are used in "user_libs", the "-L" flags
# may be needed in "ldflags".

# Dummy libs have their source in the "support" subdirectory. Thus if 'crt0'
# is specified, there should be a source file 'dummy-crt0.c' in the support
# directory.

# There is no need to set an unused parameter, and this file may be empty to
# set no flags.

# Parameter values which are duplicated in architecture, board, chip or
# command line are used in the following order of priority
# - default value
# - architecture specific value
# - chip specific value
# - board specific value
# - command line value

# For flags, this priority is applied to individual flags, not the complete
# list of flags.

cflags = [
    '-c',  '-O2', '-fdata-sections', '-ffunction-sections'
]
ldflags = [
    '-O2', '-Wl,-gc-sections'
]
user_libs = ['m']
dummy_benchmark = 'dummy-benchmark'
