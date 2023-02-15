# Compiling Embench to WASM

## Requirements

To compile the Embench suite to WebAssembly, you need to have the following tools:

- [ ] clang and wasm-ld with support for the `wasm32` target (check `llc --version`).
- [ ] wasi-libc or [wasi-sdk](https://github.com/WebAssembly/wasi-sdk)

If you are using the [nix](https://nixos.org/) package manager, the following function generates a fully functional development shell:
<details>

    ```nix
    { pkgs ? import <nixos > {
        crossSystem = {
            config = "wasm32-unknown-wasi";
            useLLVM = true;
        };
    }, lib ? import <nixos/lib>, native ? import <nixos> {}} :
    let pypackages = p: with p; [
        pyelftools
    ];
    in
    pkgs.callPackage (
        {mkShell, llvm, musl, lld, wabt} :
        mkShell {
            nativeBuildInputs = [ wabt lld (native.python3.withPackages pypackages) ];
            buildInputs = [ pkgs.wasilibc ];
        }
    ) {}
    ```

</details>

## Build Steps

To build each benchmark, make sure to invoke the compiler and linker with the wasi sysroot.
The example in [arch.cfg](./arch.cfg) assumes the sysroot and target are set by the toolchain wrapper, as would be the case with wasi-sdk.

You might have to change the __compiler's name__ and the __--sysroot__, and __--target__ options depending on if you use wrapped clang or not.

Build with: `./build_all.py --arch wasm --chip generic --board generic --clean`

## Running Benchmarks

To run each benchmark, you will have to first execute the exported `_initialize` function, followed by invoking `_start`.

### Timing Benchmarks

To time benchmarks, remove the empty `start_trigger` and `stop_trigger` definitions from [boardsupport.c](./boards/generic/boardsupport.c)
and modify their declarations in [support.h](../../support/support.h) to the following:
```c
void __attribute__((import_name("start_trigger"))) start_trigger (void);
void __attribute__((import_name("stop_trigger"))) stop_trigger (void);
```
You can then provide them by the runtime/embedder.

## WASI

Embench does not currently call any WASI functions, although some modules require their imports due to tansitive dependencies from libc.
If you enable debugging, `printf` calls will be added to some benchmarks, thus requiring you to provide WASI bindings.