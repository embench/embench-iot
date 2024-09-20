# Configuration

## Building

Wasm3:
```sh
scons --config-dir=examples/wasm32/size/ cc=wasm32-unknown-wasi-clang ld=wasm32-unknown-wasi-clang user_libs=-lm cflags="-Os -fdata-sections -ffunction-sections -static -DHAVE_BOARDSUPPORT_H" ldflags="-Os -Wl,--allow-undefined,--initial-memory=65536,-gc-sections,-zstack-size=16000,--no-entry,--export=_run,--export=__heap_base,--export=__data_end,--strip-all -static -nolibc -mexec-model=reactor"
```

WAMR Standalone:
```sh
scons --config-dir=examples/wasm32/size/ cc=wasm32-unknown-wasi-clang ld=wasm32-unknown-wasi-clang user_libs=-lm cflags="-Os -fdata-sections -ffunction-sections -static -DHAVE_BOARDSUPPORT_H -Wl,--strip-all,-gc-sections,--no-entry" ldflags="-Os -Wl,--initial-memory=65536,-gc-sections,-zstack-size=16000,--no-entry,--export=_run,--export=__heap_base,--export=__data_end,--export=malloc,--export=free,--strip-all -mexec-model=reactor" --binary-extension=.wasm
```

WAMR Semihosted:
```sh
scons --config-dir=examples/wasm32/size/ cc=wasm32-unknown-wasi-clang ld=wasm32-unknown-wasi-clang user_libs=-lm cflags="-Os -fdata-sections -ffunction-sections -static -DHAVE_BOARDSUPPORT_H" ldflags="-Os -Wl,--allow-undefined,--initial-memory=65536,-gc-sections,-zstack-size=16000,--no-entry,--export=_run,--export=__heap_base,--export=__data_end,--strip-all -static -nolibc -mexec-model=reactor" --binary-extension=.wasm
```