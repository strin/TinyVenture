global_env = dict()

def compute(x, env=global_env):
    env['x'] = x

def call(env=global_env):
    newenv = global_env.copy()
    compute(1, env=newenv)
    print newenv['x']

call()