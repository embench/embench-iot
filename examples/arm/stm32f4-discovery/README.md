# Arm STM32F407

This is the reference board used for the baseline statistics of Embench IoT version 2.0. The code is compiled with the following standard tool chain component releases.

- GCC 14.1.0
- Binutils 2.39
- Newlib 4.3.0

The commands are the reference configuration for code speed and code size.  If built using the above tool chain, these should give a reference speed for all benchmarks of 1.0.

## Building the Arm support library

This only need to be done once. It is not ideal, but this library is always built in tree.

```sh
pushd examples/arm/stm32f4-discovery
make
popd
```

## Building for speed

If you haven't already done it, build the Arm support library (see above)

Then you can build the benchmarks.  The compilation options here are those used for the baseline Embench 2.0 results.
```sh
cflags="-O2 -ffunction-sections -fdata-sections -mcpu=cortex-m4 \
  mfloat-abi=soft -mthumb"
ldflags="-O2 -Wl,--gc-sections -mcpu=cortex-m4 -mfloat-abi=soft \
  -mthumb \
  -T\${CONFIG_DIR}/STM32F407IGHX_FLASH.ld -L\${CONFIG_DIR} \
  -static -nostartfiles"
scons --config-dir=examples/arm/stm32f4-discovery/ \
  --build-dir=bd-arm-gcc-14.0.1-speed \
  cc=arm32-none-eabi-gcc cflags="${cflags}" \
  ldflags="${ldflags}" user_libs='m startup' gsf=16
```

## Building for size

If you haven't already done it, build the Arm support library (see above)

Then you can build the benchmarks.  The compilation options here are those used for the baseline Embench 2.0 results.
```sh
cflags="-Os -ffunction-sections -fdata-sections -mcpu=cortex-m4 \
  mfloat-abi=soft -mthumb"
ldflags="-Os -Wl,--gc-sections -mcpu=cortex-m4 -mfloat-abi=soft \
  -mthumb \
  -T\${CONFIG_DIR}/STM32F407IGHX_FLASH.ld -L\${CONFIG_DIR} \
  -static -nostartfiles"
scons --config-dir=examples/arm/stm32f4-discovery/ \
  --build-dir=bd-arm-gcc-14.0.1-size \
  cc=arm32-none-eabi-gcc cflags="${cflags}" \
  ldflags="${ldflags}" user_libs='m startup' gsf=1
```

Note that a global scale factor of 1 is always used for code size runs.

## Measuring speed

```sh
./benchmark_speed.py --builddir bd-arm-gcc-14.0.1-speed \
  --target-module=run_stm32f4-discovery \
  --gdb-command=gdb-multiarch --gsf=16 --cpu-mhz=16
```

## Measuring size

```sh
./benchmark_size.py --builddir bd-arm-gcc-14.0.1-size
```
