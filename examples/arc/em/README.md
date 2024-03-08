# Configuration

## Building

```sh
scons --config-dir=examples/arc/em/ cc=arc-elf32-gcc cflags="-0s -mcpu=arcem -mdiv-rem -ffunction-sections" ldflags="-Wl,-gc-sections"
```
