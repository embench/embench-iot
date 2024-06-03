# Configuration

## Building

```sh
scons --config-dir=examples/or1k/ user_libs=-lm cc=or1k-elf-gcc cflags="-c -Wall -O2 -ffunction-sections -mhard-mul -mhard-div -mhard-float -mdouble-float -mror" ldflags="-Wl,-gc-sections"
```
