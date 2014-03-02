from sivm import *
from pprint import *
import matplotlib.pyplot as plt

def test_eval():
	print eval('(ior 0 1)')

def test_flip_gaussian():
	assume('w', '(flip 0.5)')
	assume('z', '(norm w 0.5)')
	observe('z', '0.8')
	printExp(global_code)
	xlist = list()
	for i in range(100):
		infer_mh(10)
		xlist.append(sample('w'))
	print xlist
	plt.hist(xlist, weights=[0.01 for i in range(100)])
	plt.show()
	print 'w = ', sample('w')
	print 'z = ', sample('z')

def test_or():
	assume('x', '(beta 1 2)')
	assume('y', '(beta 1 2)')
	assume('w', '(add x y)')
	assume('z', '(norm w 0.1)')
	printExp(global_code)
	xlist = list()
	for i in range(100):
		infer_mh(10)
		xlist.append(sample('w'))
	print xlist
	plt.hist(xlist, 30, weights=[0.1 for i in range(100)])
	plt.show()
	print 'w = ', sample('w')
	# print 'x = ', sample('x')
	# print 'y = ', sample('y')
	print 'z = ', sample('z')
	# print 'acc = ', acc
	# print 'x = ', sample('x')
	# print 'y = ', sample('y')
	# print 'z = ', sample('z')

def test_xrp():
	assume('x', '(beta 2 2)')
	pprint(global_block)
	print likelihood(global_block[0][1])


def test_reeval():
	assume('x', '(beta 1 2)')
	assume('y', '(beta 1 2)')
	assume('z', '(add x y)')
	assume('ob', '(norm z 1)')
	observe('ob', 0.5)
	pprint(global_block)
	eval(global_block)
	print 
	pprint(global_block)

def test_case_001():
	assume('x', '(beta 1 2)')
	assume('y', '(beta 1 2)')
	assume('z', '(add x y)')
	assume('ob', '(norm z 0.1)')
	observe('ob', 0.5)
	infer_mh(30)
	# pprint(global_block)
	xlist = list()
	ylist = list()
	for i in range(1000):
		xlist.append(sample('x'))
		ylist.append(sample('y'))
	plt.hist(xlist, 30)
	plt.show()
	plt.hist(ylist, 30)
	plt.show()
	print 'joint likelihood = ', likelihood(global_block)

"test case from venturecxx"
def test_case_sprinkler():
	assume("rain","(bernoulli 0.2)")
	assume("sprinkler","(bernoulli (if rain 0.01 0.4))")
	assume("grassWet","""
(bernoulli
 (if rain
   (if sprinkler 0.99 0.8)
   (if sprinkler 0.9 0.00001)))
""")
	xlist = list()
	n = 100
	for i in range(n):
		infer_mh(30)
		xlist.append(sample('grassWet'))
	plt.hist(xlist, 30, weights=[1.0/n for i in range(n)])
	plt.show()
	# print sample('sprinkler')


	
# test_flip_gaussian()
# test_or()
# test_xrp()
# test_reeval()
# test_case_001()
# test_case_sprinkler()
test_case_tricky_coin()
