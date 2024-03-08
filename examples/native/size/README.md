# Configuration

## Building

```sh
scons --config-dir=examples/native/size/ cflags="-Os -fdata-sections -ffunction-sections" ldflags="-Os -rdynamic -Wl,-gc-sections" user_libs=-lm
```

