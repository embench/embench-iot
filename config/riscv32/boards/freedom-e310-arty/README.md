# A Board Configuration for The Freedom E310 Arty FPGA Dev Kit

Author: Hiroo HAYASHI

Copyright (C) 2021 Hiroo HAYASHI

This document is part of Embench.
It is made freely available under the terms of the GNU Free Documentation
License version 1.2 or later.

Embench is a trade mark of the Embench Task Group of the Free and Open Source
Silicon Foundation.

***

This configuration demonstrates how to run the Embench on an FPGA board.
No performance tuning is done.  Your contributions are welcome.

## Requirements

- [Digilent Arty A7 100T Reference board](https://digilent.com/reference/programmable-logic/arty-a7/start)
- [The Freedom E310 Arty FPGA Dev Kit](https://github.com/sifive/freedom#freedom-e300-arty-fpga-dev-kit)
  - The data memory size of the default configuration for Arty A7 35T is too small for the Embench.
    See [Configuring FPGA](#FPGA) for details.
- [SiFive Freedom E SDK](https://github.com/sifive/freedom-e-sdk)

## Configuring FPGA

See the following links.

- [The Freedom E310 Arty FPGA Dev Kit](https://github.com/sifive/freedom#freedom-e300-arty-fpga-dev-kit)
- [Running a RISC-V Processor on the Arty A7](https://digilent.com/reference/programmable-logic/arty-a7/arty_a7_100_risc_v/start)

Notes:

- `vlsi_rom_gen` script fails with python3.5 or higher.
  [Here](https://github.com/hex-five/multizone-fpga/issues/9) is a workaround.
  See [this](https://github.com/chipsalliance/rocket-chip/issues/1991) for more details.
- The baud rate of UART is 57600 instead of 115200 as documented.
  See [this Q&A](https://forums.sifive.com/t/uploading-to-my-arty-board-not-working/323/21).

Make sure that the generated MCS file works. See the E310 E SDK document how to test it.

Next apply the following changes to increase the size of data memory, and build the FPGA again.

`freedom/Makefile.e300artydevkit`

```diff
@@ -6,7 +6,7 @@ MODEL := E300ArtyDevKitFPGAChip
 PROJECT := sifive.freedom.everywhere.e300artydevkit
 export CONFIG_PROJECT := sifive.freedom.everywhere.e300artydevkit
 export CONFIG := E300ArtyDevKitConfig
-export BOARD := arty
+export BOARD := arty_a7_100
 export BOOTROM_DIR := $(base_dir)/bootrom/xip

 rocketchip_dir := $(base_dir)/rocket-chip
```

`freedom/rocket-chip/src/main/scala/subsystem/Configs.scala`

```diff
@@ -85,7 +85,7 @@ class With1TinyCore extends Config((site, here, up) => {
       btb = None,
       dcache = Some(DCacheParams(
         rowBits = site(SystemBusKey).beatBits,
-        nSets = 256, // 16Kb scratchpad
+        nSets = 8192, // 512Kb scratchpad
         nWays = 1,
         nTLBEntries = 4,
         nMSHRs = 0,
```

`freedom-e-sdk/bsp/freedom-e310-arty/metal.default.lds`

```diff
@@ -12,7 +12,7 @@ ENTRY(_enter)
 MEMORY
 {
     itim (airwx) : ORIGIN = 0x8000000, LENGTH = 0x4000
-    ram (arw!xi) : ORIGIN = 0x80000000, LENGTH = 0x4000
+    ram (arw!xi) : ORIGIN = 0x80000000, LENGTH = 0x80000
     rom (irx!wa) : ORIGIN = 0x20400000, LENGTH = 0x1fc00000
 }

```

It is a kind of magic, isn't it?

See the following link for more details;

- [How to Increase the Size of the Data Memory on SiFive FE310 RISC-V](https://dloghin.medium.com/how-to-increase-the-size-of-the-data-memory-on-sifive-fe310-risc-v-f05df0f50a25)

## Running Embench

### Preparations

Set the environment variables `PATH` and etc. following the Freedom E SDK document.
Set the environment variable `FREEDOM_E_SDK_PATH` to the directory of the Freedom E SDK installed. For example;

```sh
export FREEDOM_E_SDK_PATH=/home/foo/github/freedom-e-sdk
```

If you have a Debug Adapter other than Olimex ARM-USB-TINY-H,
modify `bsp/freedom-e310-arty/openocd.cfg` as follows;

```diff
@@ -19,7 +19,7 @@ set debug_config "${protocol}_${connection}"
 switch ${debug_config} {
   jtag_probe {
     echo "Using JTAG"
-    source [find interface/ftdi/olimex-arm-usb-tiny-h.cfg]
+    source [find interface/ftdi/olimex-arm-usb-ocd-h.cfg]
     set chain_length 5
   }
   cjtag_probe {

```

### Build

```sh
./build_all.py -v --arch riscv32 --chip generic --board freedom-e310-arty --cpu-mhz=32
```

### Size Test

```sh
./benchmark_size.py
```

### Speed Test

Invoke an OpenOCD server in a terminal window.

```sh
/opt/SiFive/riscv-openocd-0.10.0-2020.12.1-x86_64-linux-ubuntu14/bin/openocd -f bsp/freedom-e310-arty/openocd.cfg
```

Run the following command in a terminal window.
(The device name `/dev/ttyUSB2` may be different on your system.)

```sh
stty -F /dev/ttyUSB2 57600
cat /dev/ttyUSB2
```

Run the speed benchmark.

```sh
./benchmark_speed.py --target-module run_freedom-e310-arty --timeout=600
```

On Windows Subsystem for Linux (WSL) invoke an OpenOCD server on Windows
and connect to it by using `--gdbserver-target` option.

```sh
./benchmark_speed.py --target-module run_freedom-e310-arty --timeout=600 --gdbserver-target $(grep -oP "(?<=nameserver ).+" /etc/resolv.conf):3333
```

## Debugging

### Debugging with GDB

Example:

```sh
... <invoke an OpenOCD server (See above)> ...
$ cat gdbconf
set confirm off
set remotetimeout 240
set remote hardware-breakpoint-limit 2
target extended-remote localhost:3333
monitor reset halt
monitor flash protect 0 64 last off
load
break _exit
$ riscv64-unknown-elf-gdb -q -x gdbconf bd/src/md5sum/md5sum
...
(gdb) run
...
```

Use `load` command to reload a recompiled program.

### Debugging in VS Code

Example of `launch.json`:

```json
        {
            "name": "(gdb) Launch Remote",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/bd/src/nbody/nbody",
            // "args": [],
            "cwd": "${workspaceRoot}",
            // "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "miDebuggerPath": "riscv64-unknown-elf-gdb",
            "miDebuggerServerAddress": "localhost:3333",
            "hardwareBreakpoints": { "require": true, "limit": 2 },
        },
```

Invoke an OpenOCD server (See above).

`Run`->`Start Debugging` (or `F5`), Select `(gdb) Launch Remote`.
Use `-exec load` command in `DEBUG CONSOLE` to reload a recompiled program.
Now you can debug a program using the common VS Code GUI.
