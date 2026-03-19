build command

```bash
scons --build-dir=bdMaroccino --config-dir=examples/openrisc/maroccino/ user_libs=-lm \
                                                         cc=or1k-elf-gcc \
                                                         cflags='-c -O3 -fdata-sections -ffunction-sections -mcmov -mhard-float -mror -mrori -msext -msfimm -mshftimm -munordered-float' \
                                                         ldflags='-O3 -Wl,-gc-sections'
```

make sure or1k-elf-gcc is in your PATH, or change the cc variable to point to the correct location of the compiler.

[TODO] Linker is faulty. `linker.ld` includes `generated/output_format.ld` and `generated/regions.ld`, so those files must exist under the selected `--config-dir`-- written by 2024 student.

Command to for benchmark_size
```bash
python benchmark_size.py --builddir bdMaroccino/ --logdir logsMaroccino --baselinedir baseline-data/
```

Command for speed results
```bash
python benchmark_speed.py --builddir bdMaroccino/ --logdir logsMaroccino --baselinedir baseline-data/ --target-module run_mor1kx --cpu-mhz 1 --timeout 600 --config-path examples/openrisc/fusesoc.conf --tool verilator --system ::mor1kx-generic:1.1 --fusesoc_target marocchino_tb
```