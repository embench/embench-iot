from pathlib import Path
import sys
Import('env')

bd = env['BUILD_DIR']

startup = [env.Object(str(bd / 'config/startup/crt0.S'))]
startup += env.Object(str(bd / 'config/startup/dummy.S'))
lib = env.Library(startup)

env.Prepend(LIBS=[lib])