'''
This file resolves naming inconsistencies between scipy.stats and Venture.
'''
import scipy.stats as rd
import numpy as np

"---Aliases---"
# uniform in scipy.stats takes (loc,scale) not (loc, local+scale)
class uniform_continuous:
	def __init__(self,*args):
		self.args = args
		self.rng = rd.uniform(self.args[0], self.args[1]-self.args[0])

	def update(self):
		self.rng.args = (self.args[0], self.args[1]-self.args[0])
	def rvs(self):
		self.update()
		return self.rng.rvs()
	def var(self):
		self.update
		return self.rng.var()
	def pdf(self, x):
		self.update()
		return self.rng.pdf(x)


class normal:
	def __init__(self,*args):
		self.args = args
		self.rng = rd.norm(self.args[0], np.sqrt(self.args[1]))

	def update(self):
		self.rng.args = (self.args[0], np.sqrt(self.args[1]))
	def rvs(self):
		self.update()
		return self.rng.rvs()
	def var(self):
		self.update
		return self.rng.var()
	def pdf(self, x):
		self.update()
		return self.rng.pdf(x)

def uniform_continuous_func(*args):
	return uniform_continuous(*args)

# normal in scipy.stats takes (mu,sigma) not (mu, sigma^2)
class normal:
	def __init__(self,*args):
		self.args = args
		self.rng = rd.norm(self.args[0], np.sqrt(self.args[1]))

	def update(self):
		self.rng.args = (self.args[0], np.sqrt(self.args[1]))
	def rvs(self):
		self.update()
		return self.rng.rvs()
	def var(self):
		self.update
		return self.rng.var()
	def pdf(self, x):
		self.update()
		return self.rng.pdf(x)

def normal_func(*args):
	return normal(*args)


# gamma in scipy has loc param.
class gamma:
	def __init__(self,*args):
		self.args = args
		self.rng = rd.gamma_old(self.args[0], 0, self.args[1])
	def update(self):
		self.rng.args = (self.args[0], 0, self.args[1])
	def rvs(self):
		self.update()
		return self.rng.rvs()
	def var(self):
		self.update
		return self.rng.var()
	def pdf(self, x):
		self.update()
		return self.rng.pdf(x)
def gamma_func(*args):
	return gamma(*args)


def load_aliases(op, rd):
	op.power = op.pow

	# random mapping.
	rd.flip = rd.bernoulli
	rd.flip.pdf = rd.flip.pmf
	rd.gamma_old = rd.gamma
	rd.gamma = gamma_func
	rd.normal = normal_func
	rd.uniform_continuous = uniform_continuous_func