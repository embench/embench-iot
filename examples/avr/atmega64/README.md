# Configuration

## Building

```sh
scons --config-dir=examples/avr/atmega64 cc=avr-elf-gcc cflags="-ggdb3 -fdata-sections -ffunction-sections" ldflags="-Wl,-gc-sections"
```
