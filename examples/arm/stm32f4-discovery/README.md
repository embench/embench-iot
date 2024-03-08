# Configuration

## Building

Note: you will need to compile and include the startup code as a user library.

```sh
scons --config-dir=examples/arm/stm32f4-discovery/ cc=arm-none-eabi-gcc ldflags="-T\${CONFIG_DIR}/STM32F407XG.ld"
```
