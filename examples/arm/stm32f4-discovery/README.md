# Configuration

## Building

Note: you will need to compile and include the startup code as a user library.

```sh
cd examples/arm/stm32f4-discovery
make
cd -
scons --config-dir=examples/arm/stm32f4-discovery/ cc=arm-none-eabi-gcc cflags='-O2 -flto -ffunction-sections -fdata-sections -mcpu=cortex-m4 -mthumb' \
  ldflags='-O2 -Wl,--gc-sections -flto -mthumb -mcpu=cortex-m4 -T${CONFIG_DIR}/STM32F407IGHX_FLASH.ld -L${CONFIG_DIR} -static -nostartfiles' user_libs='m startup' cpu_mhz=16
```

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
```
