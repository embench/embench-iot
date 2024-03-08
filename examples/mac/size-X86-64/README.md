# Configuration

## Building

```sh
scons --config-dir=examples/mac/size-X86-64 cflags="-Os -fdata-sections -ffunction-sections -target x86_64-apple-macos11.1 -Wincompatible-library-redeclaration -D_FORTIFY_SOURCE=0" \
    ldflags="-Os -rdynamic -Wl,-dead_strip -target x86_64-apple-macos11.1" user_libs=-lm
```
