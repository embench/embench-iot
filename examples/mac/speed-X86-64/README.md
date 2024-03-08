# Configuration

## Building

```sh
scons --config-dir=examples/mac/speed-X86_64 cflags="-O2 -fdata-sections -ffunction-sections -target x86_64-apple-macos11.1" \
    ldflags="-O2 -Wl,-dead_strip -target x86_64-apple-macos11.1" user_libs=-lm
```
