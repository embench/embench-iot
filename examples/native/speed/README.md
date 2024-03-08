# Configuration

## Building

```sh
scons --config-dir=examples/native/speed/ cflags="-O2 -fdata-sections -ffunction-sections" ldflags="-O2 -Wl,-gc-sections" user_libs=-lm
```

