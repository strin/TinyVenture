from sivm import *
from parser import *

def test_env():
    a = Env()
    a['1'] = 1
    a['2'] = 2
    b = Env(a)
    print b['1']
    b['1'] = 'hello'
    b['3'] = 'mit'
    print b['1']
    print b['2']
    print b['3']

def test_compile():
    x = parse('(begin (lambda () (beta 1 (flip 0.5))) (lambda (v) (flip v)))')
    compile(x)
    printExp(x)

def test_search_xrp():
	print 'env.name = ', global_env.name
	print searchXrp([Symbol('flip'), '1', 0.5], global_env)
	global_env.set('a', 3, 'top_1')
	print searchXrp(Symbol('a'), global_env)
	global_env.set('b', lambda x: x+1, 'top_2')
	print searchXrp([Symbol('b')], global_env)
	print searchXrp([Keyword('lambda'), 'f1', [], [Symbol('flip'), 'x', 0.5]], global_env)


# test_env()
# test_compile()
test_search_xrp()
