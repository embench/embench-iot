# This are the instructions for using Embench on a Macintosh

These instructions cover both Intel and Apple Silicon Macs

## Size benchmarks

As the Mac uses Mach-O files for executables the current scripts which assume ELF
do not work. **This is work to be done.**

## Speed benchmarks

### Building the speed benchmarks

The benchmarks can be built for x86 or ARM on either type of Mac

To build for x86: `./build_all.py --arch mac --chip speed-test-clang-X86-64`

To build for ARM `./build_all.py --arch mac --chip speed-test-clang-ARM-M1`

### Running the speed benchmarks

To run the current build `./benchmark_speed.py --target-module run_mac`

Note that you can run both x86 and ARM
builds on an Apple Silicon Mac, but you can only run a x86 build on an Intel Mac.
