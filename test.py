import sivm
from parser import *
import argparse
import numpy as np
import scipy.stats as sp
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('-x', nargs=1)
parser.add_argument('-t', nargs=1)
args = parser.parse_args()

def init():
    if args.x[0] == "venture":
        import venture.shortcuts as vs 
        v= vs.make_church_prime_ripl()
    elif args.x[0] == "tiny":
        v=sivm.TinySIVM()
    else:
        exit()
    return v

class Test:
	def posterior_samples(self, v, var_name,no_samples,int_mh):
		s=[]
		for sample in range(no_samples): #v.restart()
			print 'sample = ', sample
			v.infer(int_mh)
			label = var_name + str(np.random.randint(10**5))+str(sample)
			v.predict(var_name,label)
			s.append(v.report(label))
		return s
    
	def test_five_heads(self):
		v = init()
		v.assume("is_tricky", "(flip 0.1)")
		v.assume("theta", "(if is_tricky (beta 1.0 1.0) 0.5)")
		v.assume("flip_coin","(lambda () (flip theta) ) ")
		[v.observe('(flip_coin)', 'true') for j in range(5)]
		is_tricky_samples=self.posterior_samples(v, 'is_tricky',no_samples=50,int_mh=10)
		t_is_tricky =.372   # true value (analytically computed)
		diff=abs(np.mean(is_tricky_samples) - t_is_tricky)
		print 'true P(is_tricky)=%.3f; estimated P(is_tricky)=%.3f' % (t_is_tricky,np.mean(is_tricky_samples))
		assert diff < .08 ,'difference > .08'

	def test_five_tails(self):
		v = init()
		v.assume("is_tricky", "(flip 0.1)")
		v.assume("theta", "(if is_tricky (beta 1.0 1.0) 0.5)")
		v.assume("flip_coin","(lambda () (flip theta) ) ")	
		[v.observe('(flip_coin)', 'true') for j in range(5)]
		[v.observe('(flip_coin)', 'false') for j in range(5)]
		is_tricky_samples=self.posterior_samples(v, 'is_tricky',no_samples=50,int_mh=10)
		t_is_tricky = .04
		diff=abs(np.mean(is_tricky_samples) - t_is_tricky)
		print 'true P(is_tricky)=%.3f; estimated P(is_tricky)=%.3f' % (t_is_tricky,np.mean(is_tricky_samples))
		assert diff < .03 ,'difference > .03'

	def test_suspicion(self):
		v = init()
		v.assume("is_tricky", "(flip 0.5)")
		v.assume("theta", "(if is_tricky (beta .4 .4) 0.5)")
		v.assume("flip_coin","(lambda () (flip theta) ) ")
		[v.observe('(flip_coin)', 'true') for j in range(5)]

		is_tricky_samples=self.posterior_samples(v, 'is_tricky',no_samples=100,int_mh=10)

		t_is_tricky = .89   # true value (analytically computed)
		diff=abs(np.mean(is_tricky_samples) - t_is_tricky)
		print 'true P(is_tricky)=%.3f; estimated P(is_tricky)=%.3f' % (np.mean(is_tricky_samples), t_is_tricky)
		assert diff < .05 ,'difference > .05'

	def test_infer_mean(self):
		v = init()
		v.assume('get_mu','(normal 0 1)')
		v.assume('get_x','(lambda () (normal get_mu 1))')
		v.observe('(get_x)','5.0')
		v.observe('(get_x)','6.0')

		mu_samples=self.posterior_samples(v, 'get_mu',no_samples=100,int_mh=100)

		true_e_mu=3.7; true_sd_mu = .58    # true value (analytically computed)
		diff=abs(np.mean(mu_samples) - true_e_mu)
		print 'true E(mu / D)=%.2f; estimated =%.3f' % (true_e_mu, np.mean(mu_samples))

		x=np.arange(1,6,.1)
		y=sp.norm.pdf(x,loc=true_e_mu,scale=true_sd_mu)
		plt.plot(x,y)
		plt.hist(mu_samples,bins=15,normed=True)
		plt.title('Histograpm of Posterior samples of Mu vs. True Posterior on Mu')
		plt.xlabel('Mu'); plt.ylabel('P(mu / data)')
		plt.show()

		assert diff < .5 ,'difference > .5'

	def test_infer_variance(self):
		v = init()
		v.assume('get_prec','(gamma 1 1)')
		v.assume('get_x','(lambda () (normal 0 (power get_prec -.5)))')
		v.observe('(get_x)','5.0')
		v.observe('(get_x)','-5.0')
		prec_samples=self.posterior_samples(v, 'get_prec',no_samples=100,int_mh=10)

		true_a_prec=2.0; true_b_prec = 26.0;    # true values (analytically computed)
		diff=abs(np.mean(prec_samples) - (true_a_prec / true_b_prec))     # mean of Ga(a,b)=a/b
		print 'true E(prec / D)=%.2f; estimated =%.3f' % ((true_a_prec / true_b_prec),np.mean(prec_samples))
		print 'true v(prec / D)=%.4f; estimated =%.4f' % ( (true_a_prec / (true_b_prec**2)),np.var(prec_samples) )

		plt.hist(prec_samples,bins=20,normed=True)
		plt.show()
		print '\n Compare histogram to Gamma(2,26), which has mean=.1 and variance=.003.'

		assert diff < .2 ,'difference > .2'

	def test_infer_gamma_normal(self):
		v = init()
		v.assume('scale','(gamma 10 .01)')
		v.assume('get_mu','(normal 0 1)')
		v.assume('get_x','(lambda () (normal get_mu 1))')
		v.observe('(get_x)','5.0')
		v.observe('(get_x)','6.0')
		v.observe('(get_x)','4.5')

		mu_samples=self.posterior_samples(v, 'get_mu',no_samples=100,int_mh=10)

		true_e_mu=3.7; true_sd_mu = .58  # true values when the scale is fixed at 1
		x=np.arange(1,6,.1)
		y=sp.norm.pdf(x,loc=true_e_mu,scale=true_sd_mu)
		plt.plot(x,y)
		plt.hist(mu_samples,bins=20,normed=True)
		plt.title('Histogram of posterior samples of mu vs. posterior on mu if scale parameter was already known')
		plt.show()

		diff=abs(np.mean(mu_samples) - true_e_mu)
		print 'We compare to model that already knows a good scale parameter.\n True E(mu / D)=%.2f; estimated =%.3f' % (true_e_mu, np.mean(mu_samples))
		assert diff < 2 ,'difference > 2'

	def test_bayes_linear_reg(self):
		v = init()
		v.assume('w0','(normal 0 1)')
		v.assume('w1','(normal 0 1)')
		v.assume('noise','.05')
		v.assume('get_y','(lambda (x) (normal (+ w0 (* x w1)) noise ) )') 
		v.observe('(get_y 2.)','5.0')
		v.observe('(get_y -3.)','-4.95')
		w0_samples=self.posterior_samples(v, 'w0',no_samples=100,int_mh=10)
		w1_samples=self.posterior_samples(v, 'w1',no_samples=100,int_mh=10)

		true_w0=1; true_w1=2
		diff0=abs(np.mean(w0_samples) - true_w0)
		diff1=abs(np.mean(w1_samples) - true_w1)
		print 'true E(w0 / D)=%.3f; estimated =%.3f' % (true_w0, np.mean(w0_samples))
		print 'true E(w1 / D)=%.3f; estimated =%.3f' % (true_w1, np.mean(w1_samples))
		assert (diff0 < .2 and diff1 < .2),'one of diffs > .2'

	def test_bayes_disc_reg_1(self):
		v = init()
		v.assume('w0','(normal 0 1)')
		v.assume('w1','(normal 0 1)')
		v.assume('noise','(uniform_continuous .01 2.)')
		v.assume('get_y','(lambda (x) (normal (+ w0 (* x w1)) noise ) )') 
		v.observe('(get_y 2.)','5.0')
		v.observe('(get_y -3.)','-4.95')
		v.observe('(get_y 6.)','13.02')
		v.observe('(get_y 0)','.99')

		noise_samples=self.posterior_samples(v, 'noise',no_samples=50,int_mh=10)
		w0_samples=self.posterior_samples(v,'w0',no_samples=50,int_mh=10)
		w1_samples=self.posterior_samples(v,'w1',no_samples=50,int_mh=10)

		true_w0=1; true_w1=2; true_noise=.05
		diff0=abs(np.mean(w0_samples) - true_w0)
		diff1=abs(np.mean(w1_samples) - true_w1)
		diff2=abs(np.mean(noise_samples) - true_noise)
		print 'true E(w0 / D)=%.3f; estimated =%.3f' % (true_w0, np.mean(w0_samples))
		print 'true E(w1 / D)=%.3f; estimated =%.3f' % (true_w1, np.mean(w1_samples))
		print 'true noise=%.3f; estimated =%.3f' % (true_noise, np.mean(noise_samples))
		assert (diff0 < .2 and (diff1 < .2 and diff2 < .2)),'one of diffs > .2'
		
	def test_bayes_disc_reg_2(self):
		v = init()

		v.assume('mu','(normal 0 2)')
		v.assume('get_x','(lambda () (normal mu 1))')

		v.assume('w0','(normal 0 1)')
		v.assume('w1','(normal 0 1)')
		v.assume('noise','.05')
		v.assume('get_y','(lambda (x) (normal (+ w0 (* x w1)) noise ) )') 

		xnames=['x1','x2','x3']; 
		xvals=[2.0,-3.0,6.0]; 
		yvals=[5.0,-4.95,13.12];
		[v.assume(xname,'(get_x)') for xname in xnames]
		[v.observe(xname,str(xval)) for xname,xval in zip(xnames,xvals)]
		[v.observe('(get_y '+xname+')',str(yval)) for xname,yval in zip(xnames,yvals)]

		w0_samples=self.posterior_samples(v, 'w0',no_samples=100,int_mh=10)
		w1_samples=self.posterior_samples(v, 'w1',no_samples=100,int_mh=10)

		true_w0=1; true_w1=2; true_noise=.05
		diff0=abs(np.mean(w0_samples) - true_w0)
		diff1=abs(np.mean(w1_samples) - true_w1)
		print 'true E(w0 / D)=%.3f; estimated =%.3f' % (true_w0, np.mean(w0_samples))
		print 'true E(w1 / D)=%.3f; estimated =%.3f' % (true_w1, np.mean(w1_samples))
		assert (diff0 < .2 and diff1 < .2),'one of diffs > .2'

	def test_mem(self):
		v = init()

		v.assume('flip_coin', '(mem (lambda (x) (flip x)))')
		[v.assume('x'+str(i), '(flip_coin 0.3)') for i in range(100)]
		v.eval(v.global_code)

		xlist = [v.predict('x'+str(i), 'x'+str(i)) for i in range(100)]
		print xlist

test = Test()
getattr(Test, args.t[0])(test)

