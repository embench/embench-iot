# RISC-V CV32E40Pv2 FPGA

This is the configuration for the OpenHW Group CV32E40Pv2 core combined with a standard RISC-V debug unit.  The configuration was tested using X-HEEP on a Nexys A7 FPGA.

## Building the benchmarks

### Building for speed

The compilation options here are those used for the Embench 2.0 speed measurement.
```sh
cflags="-O2 -ffunction-sections -fdata-sections -march=rv32imc_zicsr \
  -mabi=ilp32"
ldflags="'-O2 -march=rv32imc_zicsr -mabi=ilp32 -Wl,--gc-sections \
  -static -T${CONFIG_DIR}/link.ld"
scons --config-dir=examples/riscv32/cv32e40pv2fpga/ \
  --build-dir=bd-riscv-gcc-speed \
  cc=riscv32-unknown-elf-gcc cflags="${cflags}" \
  ldflags="${ldflags}" user_libs='m' gsf=15
```

The link file is for an X-HEEP configuration with 32kiB of ROM and 64kiB RAM.
We provide an alternative (`unilink.ld`) for a unified memory space of 96kiB (slower). A different FPGA may require modifications.  We assume the FPGA has been configured with the FPGA and is attached to the computer via a HS2 adapter.

### Building for size

Then you can build the benchmarks.  The compilation options here are those used for the baseline Embench 2.0 results.
```sh
cflags="-Os -msave-restore -ffunction-sections -fdata-sections \
  -march=rv32imc_zicsr -mabi=ilp32"
ldflags="-Os -msave-restore -march=rv32imc_zicsr -mabi=ilp32 \
  -Wl,--gc-sections -static -T${CONFIG_DIR}/link.ld"
scons --config-dir=examples/riscv32/cv32e40pv2fpga/ \
  --build-dir=bd-riscv-gcc-size \
  cc=riscv32-unknown-elf-gcc cflags="${cflags}" \
  ldflags="${ldflags}" user_libs='m' gsf=1
```

Note that a global scale factor of 1 is always used for code size runs.

## Measuring the benchmarks

## Setting up the debug server

Pre-requisite is OpenOCD 12 or later.

Before starting benchmarking for speed, a debug server for the FPGA is used.  In a separate terminal run.
```
cd examples/riscv32/cv32e40pv2fpga
openocd -f openocd-nexys-hs2.cfg
```

## Measuring speed

```sh
./benchmark_speed.py --builddir bd-riscv-gcc-speed \
  --target-module=run_xheep_gdbserver_fpga \
  --gdb-command=riscv32-unknown-elf-gdb --gsf=15 --cpu-mhz=15
```

## Measuring size

```sh
./benchmark_size.py --builddir bd-riscv-gcc-size
```
