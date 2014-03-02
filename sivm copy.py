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
rd.flip.pdf = rd.flip.pmf
ist = isinstance

"---Global Environment---"
counter_lambda = [0]  # naming counter for lambda expression.
counter_xrp = [0]	  # naming counter for xrp.
cat = lambda outer, name: outer+'_'+name if name != None else None # concatenation rule for naming.
xrp_db = dict()

class Env(dict):
	def __init__(self, outer=None, params = (), args = (), name = 'top'):
		self.update(zip(params, args))
		self.outer = outer
		self.name = cat(outer.name, name) if outer != None else name

	def get(self, var):
		if super(Env, self).has_key(var):
			return super(Env, self).__getitem__(var)
		else:
			return self.outer.get(var)

	def set(self, var, v, expr = None):
		super(Env, self).__setitem__(var, {'v':v, 'e':expr})

	def __getitem__(self, var):
		ans = self.get(var)
		if ist(ans, dict):
			return ans['v']
		else:
			return ans

	def getExpr(self, var):
		return self.get(var)['e']

	def __setitem__(self, var, v):
		self.set(var, v)


def TinyRIPL():
	def __init__():
		self.global_env = Env()
		xrp = vars(rd) 		           # exchangable random primitives.
		self.global_env.update(vars(math))  # basic math ops: sin, cos.
		self.global_env.update(xrp)         # elementary random primitives.
		self.global_env.update(vars(op))    # basic ops: +,-,...

		self.global_code = makeBeginStmt()  # code and trace.

	"---function types---"
	is_var_ref = lambda x : not ist(x, list) and ist(x, Symbol) and not xrp.has_key(x.name)
	is_xrp_ref = lambda x : not ist(x, list) and ist(x, Symbol) and xrp.has_key(x.name)	
	is_keyword = lambda x, keyword: ist(x, list) and ist(x[0], Keyword) and x[0].name == keyword
	is_literal = lambda x : not ist(x, list) and not ist(x, Symbol)
	is_func = lambda x : ist(x, list) and ist(x[0], Symbol) and not xrp.has_key(x[0].name)

	"---Proposal Kernels---"
	# return (x', F, R)
	def proposal(proc):
		if hasattr(proc ,'family') and ist(proc.family, rd.distributions.bernoulli_gen):
			xp = rd.bernoulli(0.5).rvs()
			F = R = np.log(0.5)
		else:
			xp = proc.rvs()
			F = np.log(proc.pdf(xp))
			R = np.log(proc.pdf(proc.val))
		return (xp, F, R)

	"---Main Algorithm---"
	def compile(x, clambda = counter_lambda, cxrp = counter_xrp):
		if ist(x, list) and len(x) > 0:
			if is_func(x):
				x.insert(1, 'f'+str(counter_lambda[0]))
				counter_lambda[0] = counter_lambda[0]+1
			elif xrp.has_key(str(x[0])):
				x.insert(1, str(counter_xrp[0]))
				counter_xrp[0] = counter_xrp[0]+1
			for exp in x:
				compile(exp, clambda, cxrp)

	def searchXrp(exp, env):
		related_xrp = None
		if is_var_ref(exp):
			related_xrp = env.getExpr(exp.name)
		elif ist(exp, list) and is_keyword(exp, "lambda") and is_xrp_ref(exp[2][0]):
			related_xrp = exp[2][1]
		elif ist(exp, list) and is_xrp_ref(exp[0]):
			related_xrp = cat(env.name, exp[1])
		elif is_func(exp):
			related_xrp = cat(env.name, cat(exp[1], env.getExpr(exp[0].name)))
		return related_xrp

	def eval(x, env = self.global_env, db = xrp_db):
		# "elementary unit"
		if is_xrp_ref(x):
			return (x.name, 0)
		elif is_var_ref(x):
			return (env[x.name], 0)
		elif is_literal(x): 				          # literal
			return (x, 0)
		# "functions"
		elif is_keyword(x, "define") or is_keyword(x, "set"):
			(_, var, exp) = x
			(val, lhood2) = eval(exp, env, db)
			env.set(str(var), val, searchXrp(exp, env))
			return (env[str(var)], lhood2)
		elif is_keyword(x, "observe"):
			(_, var, exp) = x
			
			xrp_name = searchXrp(var, env)
			(val, lhood0) = eval(var, env, db)
			if db.has_key(xrp_name):
				(db[xrp_name].ob, lhood) = eval(exp, env, db)
				lhood = lhood-db[xrp_name].lhood
				db[xrp_name].lhood = np.log(db[xrp_name].pdf(db[xrp_name].ob))
				lhood = lhood+db[xrp_name].lhood
				env[str(var)] = db[xrp_name].ob
				return (db[xrp_name].ob, lhood+lhood0)
			else:
				print "error: only xrp outcome can be observed."
				return (val, lhood0)
		elif is_keyword(x, "if"):
			(_, test, conseq, alt) = x
			(testval, lhood1) = eval(test, env, db)
			(res, lhood2) = eval((conseq if testval else alt), env, db)
			return (res, lhood1+lhood2)
		elif is_keyword(x, "lambda"):
			(_, var, exp) = x
			return (lambda name, *args: eval(exp, Env(env, var, args, name), db), 0)
		elif is_keyword(x, "begin"):
			lhood = 0
			for exp in x[1:]:
				(val, lhoodx) = eval(exp, env, db)
				lhood = lhood+lhoodx
			return (val, lhood)
		else:                          # (proc exp*)
			(exps, lhood) = zip(*[eval(t, env, db) for t in x])
			exps = list(exps)
			lhood = sum(lhood)
			procsym = exps.pop(0)
			name = exps.pop(0)
			if ist(procsym, str) and xrp.has_key(procsym):
				if not db.has_key(cat(env.name, name)):
					proc = xrp[procsym](*exps)
					proc.family = xrp[procsym]
					proc.val = proc.rvs()
					db[cat(env.name, name)] = proc
				else:
					proc = db[cat(env.name, name)]
					proc.args = exps
				recent_xrp = proc
				if hasattr(proc, 'ob'):
					proc.val = proc.ob
				if proc.pdf(proc.val) == 0: # overflow.
					proc.lhood = float('-inf')	
				else:
					proc.lhood = np.log(proc.pdf(proc.val))
				lhood = lhood+proc.lhood
				return (proc.val, lhood)
			else:
				if ist(procsym, types.LambdaType):
					(val, lhood0) = procsym(name, *exps)
				else:
					(val, lhood0) = procsym(*exps)
				return (val, lhood+lhood0) 
			

	def assume(var, raw_expr):
		stmt = makeDefineStmt(var, parse(raw_expr))
		compile(stmt)
		self.global_code.append(stmt)

	def observe(var, raw_expr, code=self.global_code, env=self.global_env):
		print parse(var)
		stmt = makeObserveStmt(parse(var), parse(raw_expr))
		compile(stmt)
		code.append(stmt)

	"inference through MH (lightweight implementation)"
	def infer_mh(num_iter, code=self.global_code, env=self.global_env, verbose = False):
		(_, ll) = eval(self.global_code, env, xrp_db)
		for it in range(num_iter):
			for name in xrp_db.keys():
				db = copy.deepcopy(xrp_db)
				newenv = Env(env)
				proc = db[name]
				if hasattr(proc, 'ob'):
					continue
				(xp, F, R) = proposal(proc)
				proc.val = xp
				(_, llp) = eval(self.global_code, newenv, db)
				# print('R = ', R, 'F = ', F, 'llp = ', llp, 'll = ', ll)
				if np.log(rd.uniform().rvs()) < llp-ll+R-F: # accept.
					# print 'acc'
					xrp_db.update(db)
					env.update(newenv)
					ll = llp

	def sample(var, code=self.global_code, env=self.global_env):
		# infer_mh(-1)
		return env[var]






