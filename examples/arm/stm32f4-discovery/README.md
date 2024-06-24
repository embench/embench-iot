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
scons --config-dir=examples/arm/stm32f4-discovery/ cc=arm-none-eabi-gcc cflags='-O2 -mcpu=cortex-m4 -mthumb'   ldflags='-O2 -Wl,--gc-sections -mthumb -mcpu=cortex-m4 -T${CONFIG_DIR}/STM32F407IGHX_FLASH.ld -L${CONFIG_DIR} -static -nostartfiles' user_libs='m startup' gsf=16
```

## Building for size

If you haven't already done it, build the Arm support library (see above)

Then you can build the benchmarks.  The compilation options here are those used for the baseline Embench 2.0 results.
```sh
scons --config-dir=examples/arm/stm32f4-discovery/ cc=arm-none-eabi-gcc cflags='-Os -mcpu=cortex-m4 -mthumb'   ldflags='-Os -Wl,--gc-sections -mthumb -mcpu=cortex-m4 -T${CONFIG_DIR}/STM32F407IGHX_FLASH.ld -L${CONFIG_DIR} -static -nostartfiles' user_libs='m startup' gsf=1
```

Note that a global scale factor of 1 is always used for code size runs.

## Measuring speed

```sh
./benchmark_speed.py --target-module=run_stm32f4-discovery --gdb-command=arm-none-eabi-gdb --cpu-mhz=16
```


## Measuring size

```sh
cd examples/arm/stm32f4-discovery
make
cd -
scons --config-dir=examples/arm/stm32f4-discovery/ cc=arm-none-eabi-gcc cflags='-Os -ffunction-sections -fdata-sections -mcpu=cortex-m4 -mthumb' \
  ldflags='-Os -Wl,--gc-sections,-export-dynamic -mthumb -mcpu=cortex-m4 -T${CONFIG_DIR}/STM32F407IGHX_FLASH.ld -L${CONFIG_DIR} -static -nostartfiles --specs=nosys.specs' user_libs='m startup'
./benchmark_size.py
```
