Command to build the benchmarks for the mor1kx configuration:

```bash
scons --build-dir=bdMor1kx --config-dir=examples/openrisc/mor1kx/ user_libs=-lm \
                                                         cc=or1k-elf-gcc \
                                                         cflags='-c -O3 -fdata-sections -ffunction-sections -mcmov -mhard-float -mror -mrori -msext -msfimm -mshftimm -munordered-float' \
                                                         ldflags='-O3 -Wl,-gc-sections'
```

make sure or1k-elf-gcc is in your PATH, or change the cc variable to point to the correct location of the compiler.

[TODO] Linker is faulty. `linker.ld` includes `generated/output_format.ld` and `generated/regions.ld`, so those files must exist under the selected `--config-dir`-- written by 2024 student.

Command to for benchmark_size
```bash
python benchmark_size.py --builddir bdMor1kx/ --logdir logsMor1kx --baselinedir baseline-data/
```

command for speed results
```bash
python benchmark_speed.py --builddir bdMor1kx/ --logdir logsMor1kx --baselinedir baseline-data/ --target-module run_mor1kx --cpu-mhz 1 --timeout 600 --config-path examples/openrisc/fusesoc.conf --tool verilator --system ::mor1kx-generic:1.1 --fusesoc_target mor1kx_tb
```