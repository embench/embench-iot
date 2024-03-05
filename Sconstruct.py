from pathlib import Path
import os

def find_benchmarks(bd):
    dir_iter = Path('src').iterdir()
    return [bench for bench in dir_iter if bench.is_dir()]

def parse_options():
    AddOption('--build-dir', nargs=1, type='string', default='bd')
    AddOption('--config-dir', nargs=1, type='string', default='config2')
    config_dir = Path(GetOption('config_dir'))

    vars = Variables(config_dir / 'config.py', ARGUMENTS)
    vars.Add('cc', default=env['CC'])
    vars.Add('cflags', default=env['CCFLAGS'])
    vars.Add('ld', default=env['LINK'])
    vars.Add('ldflags', default=env['LINKFLAGS'])
    vars.Add('user_libs', default=[])
    vars.Add('warmup_heat', default=1)
    vars.Add('cpu_mhz', default=1)
    return vars

def setup_directories(bd, config_dir):
    VariantDir(bd / "src", "src")
    VariantDir(bd / "support", "support")
    VariantDir(bd / "config", config_dir)
    SConsignFile(bd / ".sconsign.dblite")

def populate_build_env(env, vars):
    vars.Update(env)
    env.Append(CPPDEFINES={ 'WARMUP_HEAT' : '${warmup_heat}',
                            'CPU_MHZ' :     '${cpu_mhz}'})
    env.Append(CPPPATH=['support', config_dir])
    env.Replace(CCFLAGS = "${cflags}")
    env.Replace(LINKFLAGS = "${ldflags}")
    env.Replace(CC = "${cc}")
    env.Replace(LINK = "${ld}")
    env.Prepend(LIBS = "${user_libs}")

def build_support_objects(env):
    support_objects = []
    support_objects += env.Object(str(bd / 'support/main.c'))
    support_objects += env.Object(str(bd / 'support/beebsc.c'))
    support_objects += env.Object(str(bd / 'config/boardsupport.c'))
    env.Default(support_objects)
    return support_objects


# MAIN BUILD SCRIPT
env = DefaultEnvironment()
vars = parse_options()

bd = Path(GetOption('build_dir'))
config_dir = Path(GetOption('config_dir'))

setup_directories(bd, config_dir)
populate_build_env(env, vars)

# Setup Help Text
env.Help("\nCustomizable Variables:", append=True)
env.Help(vars.GenerateHelpText(env), append=True)

support_objects = build_support_objects(env)
benchmark_paths = find_benchmarks(bd)

benchmark_objects = {
    (bd / bench / bench.name): env.Object(Glob(str(bd / bench / "*.c")))
    
    for bench in benchmark_paths
}
env.Default(benchmark_objects.values())

for benchname, objects in benchmark_objects.items():
    bench_exe = env.Program(str(benchname), objects + support_objects)
    env.Default(bench_exe)

# call user script
SConscript(config_dir / "SConscript.py", exports='env')
