# Configuration

## Building

```sh
scons --config-dir=examples/mac/speed-M1/ cflags="-O2 -fdata-sections -ffunction-sections -target arm64-apple-macos11.1" \
    ldflags="-O2 -Wl,-dead_strip -target arm64-apple-macos11.1" user_libs=-lm
```
