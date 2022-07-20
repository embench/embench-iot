# Embench&#x2122;: Open Benchmarks for Embedded Platforms

This repository contains the Embench&#x2122; free and open source benchmark
suite.  These benchmarks are designed to test the performance of deeply
embedded systems.  As such they assume the presence of no OS, minimal C
library support and in particular no output stream.

The rationale behind this benchmark is described in "Embench™: An Evolving
Benchmark Suite for Embedded IoT Computers from an Academic-Industrial
Cooperative: Towards the Long Overdue and Deserved Demise of Dhrystone" by David
Patterson, Jeremy Bennett, Palmer Dabbelt, Cesare Garlati, G. S. Madhusudan
and Trevor Mudge (see https://tmt.knect365.com/risc-v-workshop-zurich/agenda/2#software_embench-tm-a-free-benchmark-suite-for-embedded-computing-from-an-academic-industry-cooperative-towards-the-long-overdue-and-deserved-demise-of-dhrystone).

The benchmarks are largely derived from the Bristol/Embecosm Embedded
Benchmark Suite (BEEBS, see https://beebs.mageec.org/), which in turn draws
its material from various earlier projects.  A full description and user
manual is in the [`doc` directory](./doc/README.md).

## Stable benchmark versions

The following git tags may be used to select the version of the repository for
a stable release.

- `embench-0.5`
- `embench-1.0`

## Using the benchmarks

The benchmarks can be used to yield a single consistent score for the
performance of a platform and its compiler tool chain.  The mechanism for this
is described in the [user manual](./doc/README.md).

- The benchmarks should all compile to fit in 64kB of program space and use no
  more than 64kB of RAM
  - **Note.** An earlier version tried to limit RAM to 16kB, but this proved
    too restrictive.

- The measurement of execution performance is designed to use "hot" caches.
  Thus each benchmark executes its entire code several times, before starting
  a timing run.

- Execution runs are scaled to take approximately 4 second of CPU time. This
  is large enough to be accurately measured, yet means all 19 benchmarks,
  including cache warm up can be run in a few minutes.

- To facilitate execution on machines of different performance, the tests are
  scaled by the clock speed of the processor.

- The benchmarks are designed to be run on either real or simulated
  hardware. However for meaningful execution performance results any simulated
  hardware must be strictly cycle accurate.

## Structure of the repository

The top level directory contains Python scripts to build and execute the
benchmarks.  The following are the key top level directories.

- [`config`](./config): containing a directory for each
  architecture supported, and within that directory subdirectories for board
  and cpu descriptions.  Configuation data can be provided for individual CPUs
  and individual boards.
  - **Note.** The structure of the [`config`](./config) directory is proving
    overly complex, yet inflexible. It is likely it will be flattened in a
    future release of the scripts.

- [`doc`](./doc): The user manual for Embench.

- [`src`](./src): The source for the benchmarks, one directory
  per benchmark.

- [`support`](./support): The generic wrapper code for
  benchmarks, including substitutes for some library and emulation functions.

- [`pylib`](./pylib): Support code for the python scripts

## Licensing

Embench is licensed under the GNU General Public License version 3 (GPL3).
See the COPYING file for details.  Some individual benchmarks are also
available under different licenses.  See the comments in the individual source
files for details.

The code base is OpenChain compliant, with SPDX license identifiers provided
throughout.
