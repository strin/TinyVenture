"Lightweight Venture SIVM."
from parser import *
from sys import *
import types
import color
import math, operator as op, numpy as np
import scipy.stats as rd
import matplotlib.pyplot as plt
import copy
from pprint import *

"---Aliases---"
rd.flip = rd.bernoulli
ist = isinstance

"---Global Environment---"
class Env(dict):
	def __init__(self, outer=None, params = (), args = ()):
		self.update(zip(params, args))
		self.outer = outer
	def __getitem__(self, var):
		if super(Env, self).has_key(var):
			return super(Env, self).__getitem__(var)
		else:
			return self.outer[var]

global_env = Env()
xrp = vars(rd) 		   # exchangable random primitives.
global_env.update(vars(math)) # basic math ops: sin, cos.
global_env.update(xrp)        # elementary random primitives.
global_env.update(vars(op))   # basic ops: +,-,...

"---Global Trace---"
class Trace(dict):
	''' 
	self['e'] could be 1. list, then self['e'][0] would be its operation.
					   2. elementary, then self['e'] would be not a list. 
	'''
	def __init__(self, exp = None, val = None, ob = False, lhood = 0.0):
		self.update({'e':exp, 'v':val, 'o':ob, 'l':lhood})
	''' operation on trace as a function'''
	def append(x):
		self['e'].append(x)
	def last():
		return self['e'][len(self['e'])-1]
	def func():
		if ist(self['e'],list):
			return self['e'][0]
	''' auxilary functions '''
	def visualize(self, ind = 0):
		color.indent(ind)
		color.begin(color.red)
		if ist(self['e'], Symbol):
			sys.stdout.write('<symbol: '+self['e'].name+'>\n')
		elif ist(self['e'], Keyword):
			sys.stdout.write('<keyword: '+self['e'].name+'>\n')
		else:
			if ist(self['v'], rd.distributions.rv_frozen):
				sys.stdout.write('v: rv ')
			elif ist(self['v'], types.LambdaType):
				sys.stdout.write('v: lambda ')
			else:
				sys.stdout.write('v: '+str(self['v'])+' ')
			sys.stdout.write('<literal: '+str(self['e'])+'>\n')
		
		color.begin(color.green)
		sys.stdout.write('l: '+str(self['l'])+' ')
		color.begin(color.grey)
		sys.stdout.write('o: '+str(self['o'])+' ')
		color.end()
		if ist(self['e'], list):
			print
			for block in self['e']:
				visualizeTrace(block, ind+1)
		else:
		if ind == 0:
			print
	def makeFunc(name):
		self['e'] = list()
		self['e'][0] = name
	def makeSymbol(self, symbol):
		self['e'] = '<symbol: '+symbol.name+'>'
	def makeLiteral(self, literal):
		self['e'] = '<literal: '+str(literal)+'>'
		self['v'] = literal
	def makeKeyword(self, keyword):
		self['e'] = '<keyword: '+keyword.name+'>'
	def makeDefine(self, var, v):
		self.makeFunc("define")
		self.append(Trace().makeSymbol(var))
		self.append(Trace().makeLiteral(var))

	def makeCall(self, vars, args, trace):
		self.makeFunc("begin")
		for (var, arg) in zip(vars, args):
			self.append(Trace().makeDefine(var, arg))
		




global_code = []  # code and trace.
global_trace = {'e':[{'e':'begin', 'v':None, 'l':0, 'o':False}], 'v':None, 'l':0, 'o':False}

def visualizeTrace(trace, ind = 0):
	

"---Main Algorithm---"

def eval(x, env):
	trace = Trace()
	"elementary unit"
	if not ist(x, list):
		if ist(x, Symbol):             # variable reference
			ans = env[x.name]
			trace.makeSymbol(x)
			if ist(ans, Trace):
				trace['v'] = ans['v']
		else: 				          # literal
			trace.makeLiteral(x)
			trace['v'] = x
	"functions"
	else:
		trace.makeFunc(str(x[0]))
		elif ist(x[0], Keyword) and x[0].name == "define":                # (define symbol trace)
			trace.append(eval(x[1], env))
			name = trace.last()['v']
			trace.append(eval(x[2], env))
			env[str(name)] = trace.last()
			trace['v'] = trace.last()['v']
		elif ist(x[0], Keyword) and x[0].name == "if":                    # (if test conseq alt):
			(_, test, conseq, alt) = x
			trace.append(eval(test, env))
			trace.append(eval((conseq if trace.last()['v'] else alt), env))
			trace['v'] =  trace.last()['v']
		elif ist(x[0], Keyword) and x[0].name == "lambda":                # (lambda (var*) exp)
			(_, var, exp) = x
			trace['v'] =  lambda *args: eval(exp, Env(var, args, env))
		elif x[0]['e'] == "set":           # (set! var exp)
		    (_, var, exp) = x
		    env.find(str(var))[str(var)] = eval(exp, env)
		elif x[0]['e'] == "begin":          # (begin exp*)
		    for exp in x[1:]:
		        val = eval(exp, env)
			trace['v'] = val
		else:                          # (proc exp*)
			exps = [eval(t, env) for t in x]
			proc = exps.pop(0)
			if xrp.has_key(str(x[0]['e'])) and not ist(x[0]['v'], rd.distributions.rv_frozen):
				if not hasattr(proc, 'pdf'): # discrete distribution.
					proc.pdf = proc.pmf
				x[0]['v'] = proc(*exps)
				x[0]['v'].args = None
			if ist(x[0]['v'], rd.distributions.rv_frozen):  # x is a stored xrp.
				if x[0]['v'].args == None or x[0]['v'].args != tuple(exps):
					x[0]['v'].args = tuple(exps)
					if not trace['o']:
						trace['v'] = x[0]['v'].rvs()
				if x[0]['v'].pdf(trace['v']) == 0: # overflow.
					trace['l'] = float('-inf')	
				else:
					trace['l'] = np.log(x[0]['v'].pdf(trace['v']))
				# print np.log(x[0]['v'].pdf(trace['v'])), x[0]['v'].args, trace['v']
			else:
				x[0]['v'] = proc
				output =  proc(*exps)
				if trace['o'] and output != trace['v']:
					trace['l'] = float('-inf')
				else:
					trace['v'] = output
	return trace['v']

def likelihood(trace):
	if ist(trace['e'], list):
		return sum([likelihood(t) for t in trace['e']])+trace['l']
	else:
		return trace['l']

def assume(var, raw_exp, block=global_trace, env=global_env):
	stmt = {'e':[{'e':"define", 'v':None, 'o':False, 'l':0.0}, \
						{'e':var, 'v':None, 'o':False, 'l':0.0},\
						parse(raw_exp)], \
						'v':None, 'o':False, 'l':0.0}
	eval(stmt, env)
	block['e'].append(stmt)

def observe(raw_expr, val, block=global_trace, env=global_env):
	stmt = parse(raw_expr)	
	stmt['o'] = True
	stmt['v'] = val
	eval(stmt, env)
	block['e'].append(stmt)
	# if env.has_key(var):
	# 	env[var]['o'] = True
	# 	env[var]['v'] = val
	# 	eval(block, env)        # re-evaluate the block.

# def infer_reject(num_iter):
# 	for it in range(num_iter):
# 		penv = env.copy()
# 		acc = True
# 		for (var, exp) in block:
# 			env[var] = eval(exp)
# 			if not aux[var][1](penv[var]):
# 				acc = False
# 				break
# 		if acc:
# 			env.update(penv)
# 			return True
# 	return False

"inference through MH (lightweight implementation)"
def infer_mh(num_iter, block=global_trace, env=global_env):
	lhood = likelihood(block)
	it = 0
	while it != num_iter : # if num_iter < 0, we run till next accept.
		xrp_c = 1
		while True:
			pblock = copy.deepcopy(block)
			newenv = Env(env)
			pratio = [1]
			if not __infer_mh(pblock, [xrp_c], pratio):
				break
			eval(pblock, env=newenv)
			# print 'new block = '
			# pprint(pblock)
			# print 'old block = '
			# pprint(block)
			newlhood = likelihood(pblock)
			if newlhood == float('-inf'): # overflow.
				alpha = 0
			elif newlhood > lhood+pratio[0]:
				alpha = 1
			else:
				alpha = np.exp(newlhood-lhood-pratio[0])
			# print 'alpha = ', alpha
			# print 'new = %f, old = %f'%(newlhood, lhood)
			if rd.uniform(0,1).rvs() < alpha: # accept.
				# print 'accept'
				block.update(pblock)
				env.update(newenv)
				lhood = newlhood
			xrp_c = xrp_c+1
			# print env['sprinkler']['v']
			# raw_input()
		# print 'iter = %d, lhood = %f'%(it, lhood)
		it = it+1
	# pprint(block)
	global_trace.update(copy.deepcopy(block))
	global_env.update(env)


def __infer_mh(trace, counter, pratio):
	x = trace['e']
	if ist(x, list):
		if ist(x[0]['v'], rd.distributions.rv_frozen) \
			and trace['o'] == False:
			counter[0] = counter[0]-1
			if counter[0] == 0:
				pratio[0] = -np.log(x[0]['v'].pdf(trace['v']))
				trace['v'] = x[0]['v'].rvs()
				trace['l'] = np.log(x[0]['v'].pdf(trace['v']))
				pratio[0] = pratio[0]+np.log(x[0]['v'].pdf(trace['v']))
				return True
		for t in x[1:]:
			if __infer_mh(t, counter, pratio):
				return True
	return False

def sample(var, block=global_trace, env=global_env):
	# infer_mh(-1)
	return env[var]['v']






