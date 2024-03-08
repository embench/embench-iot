# Configuration

## Building

```sh
scons --config-dir=examples/mac/size-M1 cflags="-Os -fdata-sections -ffunction-sections -target arm64-apple-macos11.1 -Wincompatible-library-redeclaration -D_FORTIFY_SOURCE=0" \
    ldflags="-Os -rdynamic -Wl,-dead_strip -target arm64-apple-macos11.1" user_libs=-lm
```
