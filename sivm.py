"Lightweight Venture SIVM."
from parser import *
from sys import *
import types, copy
from aliases import *
import math, operator as op, numpy as np
import scipy.stats as rd
import matplotlib.pyplot as plt

from pprint import *

# load name aliasing, comment this to use native scipy.stats names.
load_aliases(op, rd)
op_map = {'+':op.add, '*':op.mul, '/':op.div, '-':op.sub}

ist = isinstance
cat = lambda outer, name: outer+'_'+name if name != None else None # concatenation rule for naming.
NOTHING = object()
default = lambda obj, deft : deft if obj == NOTHING else obj


class Env(dict):
	def __init__(self, outer=None, params = (), args = (), name = 'top', lets_rename = False):
		self.update(zip(params, args))
		self.outer = outer
		if lets_rename:
			self.name = name
		else:
			self.name = cat(outer.name, name) if outer != None else name

	def get(self, var):
		if super(Env, self).has_key(var):
			return super(Env, self).__getitem__(var)
		elif self.outer == None:
			return None
		else:
			return self.outer.get(var)

	def has_key(self, var):
		return self.get(var) != None

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

	def update(self, env):
		if isinstance(env, Env):
			self.name = env.name
		super(Env, self).update(env)

	def copy(self):
		env = Env()
		env.update(self)
		return env


class TinySIVM:
	"---Global Environment---"
	def __init__(self):
		self.counter_lambda = [0]  # naming counter for lambda expression.
		self.counter_xrp = [0]	  # naming counter for self.xrp.

		self.xrp_db = dict()
		self.global_env = Env()
		self.xrp = vars(rd) 		           # exchangable random primitives.
		self.global_env.update(vars(math))  # basic math ops: sin, cos.
		self.global_env.update(self.xrp)         # elementary random primitives.
		self.global_env.update(vars(op))    # basic ops: +,-,...
		self.global_env.update(op_map)

		self.global_code = makeBeginStmt()  # code and trace.
		
		self.global_predict = dict()

		# function types
		self.is_var_ref = lambda x : not ist(x, list) and ist(x, Symbol) and not self.xrp.has_key(x.name)
		self.is_xrp_ref = lambda x : not ist(x, list) and ist(x, Symbol) and self.xrp.has_key(x.name)	
		self.is_keyword = lambda x, keyword: ist(x, list) and ist(x[0], Keyword) and x[0].name == keyword
		self.is_literal = lambda x : not ist(x, list) and not ist(x, Symbol)
		self.is_func = lambda x : ist(x, list) and ist(x[0], Symbol) and not self.xrp.has_key(x[0].name)
		self.is_family = lambda proc, fam: hasattr(proc ,'family') and (proc.family == fam or \
																		(type(fam) == types.TypeType and ist(proc.family, fam)))

	"---Proposal Kernels---"
	# return (x', F, R)
	def proposal(self, proc):
		if self.is_family(proc, rd.distributions.bernoulli_gen):
			xp = rd.bernoulli(0.5).rvs()
			F = R = np.log(0.5)
		elif self.is_family(proc, rd.distributions.norm_gen) or self.is_family(proc, normal_func):
			rng = rd.norm(proc.val, np.sqrt(proc.var()))
			xp = rng.rvs()
			F = R = np.log(rng.pdf(xp))
		elif self.is_family(proc, gamma_func):
			rng = rd.norm(proc.val, np.sqrt(proc.var()))
			xp = rng.rvs()
			F = R = np.log(rng.pdf(xp))
		else:
			xp = proc.rvs()
			F = np.log(proc.pdf(xp))
			R = np.log(proc.pdf(proc.val))
		return (xp, F, R)

	"---Main Algorithm---"
	def compile(self, x, clambda = NOTHING, cxrp = NOTHING):
		clambda = default(clambda, self.counter_lambda)
		cxrp = default(cxrp, self.counter_xrp)
		if ist(x, list) and len(x) > 0:
			if self.is_func(x):
				x.insert(1, 'f'+str(self.counter_lambda[0]))
				self.counter_lambda[0] = self.counter_lambda[0]+1
			elif self.xrp.has_key(str(x[0])):
				x.insert(1, str(self.counter_xrp[0]))
				self.counter_xrp[0] = self.counter_xrp[0]+1
			for (ind, exp) in enumerate(x):
				if self.is_keyword(x, "lambda") and ind == 1:
					continue
				self.compile(exp, clambda, cxrp)

	def searchXrp(self, exp, env):
		related_xrp = None
		if self.is_var_ref(exp):
			related_xrp = env.getExpr(exp.name)
		elif ist(exp, list) and self.is_keyword(exp, "lambda") and self.is_xrp_ref(exp[2][0]):
			related_xrp = exp[2][1]
		elif ist(exp, list) and self.is_xrp_ref(exp[0]):
			related_xrp = cat(env.name, exp[1])
		elif self.is_func(exp):
			related_xrp = cat(env.name, cat(exp[1], env.getExpr(exp[0].name)))
		return related_xrp

	def eval(self, x, env = NOTHING, db = NOTHING):
		env = default(env, self.global_env)
		db = default(db, self.xrp_db)
		# "elementary unit"
		if self.is_xrp_ref(x):
			return (x.name, 0)
		elif self.is_var_ref(x):
			if not env.has_key(x.name):
				print "error: undefined referrence ", x.name
				assert False
			return (env[x.name], 0)
		elif self.is_literal(x): 				          # literal
			return (x, 0)
		# "functions"
		elif self.is_keyword(x, "define") or self.is_keyword(x, "set"):
			(_, var, exp) = x
			(val, lhood2) = self.eval(exp, env, db)
			env.set(str(var), val, self.searchXrp(exp, env))
			return (env[str(var)], lhood2)
		elif self.is_keyword(x, "observe"):
			(_, var, exp) = x
			
			xrp_name = self.searchXrp(var, env)
			(val, lhood0) = self.eval(var, env, db)
			if db.has_key(xrp_name):
				(db[xrp_name].ob, lhood) = self.eval(exp, env, db)
				lhood = lhood-db[xrp_name].lhood
				# print db[xrp_name].mean(), db[xrp_name].var(), db[xrp_name].ob
				# assert db[xrp_name].pdf(db[xrp_name].ob) != 0
				db[xrp_name].lhood = np.log(db[xrp_name].pdf(db[xrp_name].ob))
				lhood = lhood+db[xrp_name].lhood
				env[str(var)] = db[xrp_name].ob
				return (db[xrp_name].ob, lhood+lhood0)
			else:
				print "error: only self.xrp outcome can be observed."
				return (val, lhood0)
		elif self.is_keyword(x, "if"):
			(_, test, conseq, alt) = x
			(testval, lhood1) = self.eval(test, env, db)
			(res, lhood2) = self.eval((conseq if testval else alt), env, db)
			return (res, lhood1+lhood2)
		elif self.is_keyword(x, "lambda"):
			(_, var, exp) = x
			var = [v.name for v in var]
			return (lambda name, *args: self.eval(exp, Env(env, var, args, name), db), 0)
		elif self.is_keyword(x, "mem"):
			(_, (_, var, expr)) = x
			var = [v.name for v in var]
			return (lambda name, *args: self.eval(expr, Env(env, var, args, str(zip(var, args)),\
														 lets_rename=True), db), 0)
		elif self.is_keyword(x, "begin"):
			lhood = 0
			for exp in x[1:]:
				(val, lhoodx) = self.eval(exp, env, db)
				lhood = lhood+lhoodx
			return (val, lhood)
		else:                          # (proc exp*)
			(exps, lhood) = zip(*[self.eval(t, env, db) for t in x])
			exps = list(exps)
			lhood = sum(lhood)
			procsym = exps.pop(0)
			name = exps.pop(0)
			if ist(procsym, str) and self.xrp.has_key(procsym):
				if not db.has_key(cat(env.name, name)):
					proc = self.xrp[procsym](*exps)
					proc.family = self.xrp[procsym]
					proc.val = proc.rvs()
					db[cat(env.name, name)] = proc
					proc.name = cat(env.name, name)
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
					lhood = lhood+lhood0
				else:
					val = procsym(*exps)
				return (val, lhood) 
			

	def assume(self, var, raw_expr):
		stmt = makeDefineStmt(var, parse(raw_expr))
		self.compile(stmt)
		self.global_code.append(stmt)

	def observe(self, var, raw_expr, code=NOTHING, env=NOTHING):
		code = default(code, self.global_code)
		env = default(env, self.global_env)
		stmt = makeObserveStmt(parse(var), parse(raw_expr))
		self.compile(stmt)
		code.append(stmt)

	"make prediction for some labeled expression"
	def predict(self, expr, label):
		expr = parse(expr)
		self.compile(expr)
		(self.global_predict[label],_) = self.eval(expr, Env(self.global_env),copy.deepcopy(self.xrp_db))		
		return self.global_predict[label]

	"report a labeled prediction"
	def report(self, label):
		return self.global_predict[label]

	"inference interface"
	def infer(self, num_iter):
		self.infer_mh(num_iter)	

	"inference through MH (lightweight implementation)"
	def infer_mh(self, num_iter, code=NOTHING, env=NOTHING):
		code = default(code, self.global_code)
		env = default(env, self.global_env)
		(_, ll) = self.eval(self.global_code, env, self.xrp_db)
		for it in range(num_iter):
			for name in self.xrp_db.keys():
				db = copy.deepcopy(self.xrp_db)
				newenv = env.copy()
				proc = db[name]
				if hasattr(proc, 'ob'):
					continue
				(xp, F, R) = self.proposal(proc)
				proc.val = xp
				(_, llp) = self.eval(self.global_code, newenv, db)
				# print('R = ', R, 'F = ', F, 'llp = ', llp, 'll = ', ll)
				if np.log(rd.uniform().rvs()) < llp-ll+R-F: # accept.
					# print 'acc'
					self.xrp_db.update(db)
					env.update(newenv)
					ll = llp

	def sample(self, var, code=NOTHING, env=NOTHING):
		code = default(code, self.global_code)
		env = default(env, self.global_env)
		return env[var]






