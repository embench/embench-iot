# Configuration

## Building

```sh
scons --config-dir=examples/arm/staticlib/ cc=arm-none-eabihf-gcc cflags="-O2 -r -c -nostdlib --specs=nosys.specs -fno-common -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 -DHAVE_BOARDSUPPORT_H" ld=arm-none-eabihf-ar ldflags="rcs" --binary-extension=.a
```

