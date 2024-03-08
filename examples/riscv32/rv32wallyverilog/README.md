# Configuration

## Building

Note: you need to manually compile and add crt0 as a user lib.

```sh
scons --config-dir=examples/riscv32/rv32wallyverilog/ user_libs=-lm cc=riscv32-unknown-none-elf-gcc \
    cflags='-fdata-sections -ffunction-sections -mabi=ilp32d' ldflags='-Wl,-gc-sections -mabi=ilp32d -nostartfiles -T${CONFIG_DIR}/link.ld'
```
