import os
Import('env')
env = env.Clone()

objs = []

objs += Glob('./main.c')

objs += Glob('./src/core/*.c')
objs += Glob('./src/layers/*.c')
objs += Glob('./src/backends/*.c')
env.Append(CPPPATH=['./inc','./port'])
env.Append(CPPDEFINES=['USE_NNOM_OUTPUT_SAVE'])

obj = env.Object(objs)
Return('obj')
