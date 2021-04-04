# This are the instructions for using Embench on a Macintosh

These instructions cover both Intel and Apple Silicon Macs

## Size benchmarks

### Building the size benchmarks

To build for x86: `./build_all.py --arch mac --chip size-test-clang-X86-64 --board size`

To build for ARM `./build_all.py --arch mac --chip size-test-clang-ARM-M1 --board size`

### Getting size information

To size the current build `./benchmark_size.py --format macho`


## Speed benchmarks

### Building the speed benchmarks

The benchmarks can be built for x86 or ARM on either type of Mac

To build for x86: `./build_all.py --arch mac --chip speed-test-clang-X86-64`

To build for ARM `./build_all.py --arch mac --chip speed-test-clang-ARM-M1`

### Running the speed benchmarks

To run the current build `./benchmark_speed.py --target-module run_mac`

Note that you can run both x86 and ARM
builds on an Apple Silicon Mac, but you can only run a x86 build on an Intel Mac.
