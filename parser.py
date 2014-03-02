'''
parsing a lisp expression using regex.
'''
import re
import sys
import color

PLEFT = '('
PRIGHT = ')'

class Symbol:
	def __init__(self, _name):
		self.name = _name
	def __str__(self):
		return self.name

class Keyword:
	def __init__(self, _name):
		self.name = _name
	def __str__(self):
		return self.name
if not hasattr(Keyword, '__ifdefined__'):
	Keyword.__ifdefined__ = True
		
__regex__ = [["(-?[0-9]+\\.?[0-9]*) ",lambda s:float(s)],
			 ["(-?[0-9]*\\.?[0-9]+) ",lambda s:float(s)],
		 	["(\\"+PLEFT+") ", lambda s:PLEFT],
		 	["(\\"+PRIGHT+") ", lambda s:PRIGHT],
			["(true|false) ", lambda s: s=="true"],
			["(if) ", lambda s:Keyword(s)],
			["(lambda) ", lambda s:Keyword(s)],
			["(mem) ", lambda s:Keyword(s)],
			["(begin) ", lambda s:Keyword(s)],
			["(set) ", lambda s:Keyword(s)],
			["(define) ", lambda s:Keyword(s)],
			["(observe) ", lambda s:Keyword(s)],
		 	["'([^ ]+) ", lambda s:str(s)],
		 	["([^ ]+) ", lambda s:Symbol(s)]
		 	]

def __merge_regex__():
	return '|'.join([ele[0] for ele in __regex__])

def __parse_exp__(token_list, pos):
	exp = list()
	p = pos+1
	while p < len(token_list):
		token = token_list[p]
		if token == PLEFT:
			(subexp, p) = __parse_exp__(token_list, p)
			exp.append(subexp)
		elif token == PRIGHT:
			return (exp,p)
		else:
			exp.append(token)
		p = p+1
	return None

def makeDefineStmt(var, expr):
	return [Keyword("define"), Symbol(var), expr]

def makeBeginStmt(*args):
	return [Keyword("begin")]+list(args)

def makeObserveStmt(var, expr):
	return [Keyword("observe"), var, expr]

def parse(s):
	s = s.replace('\n', '')
	s = s.replace('\r', '')
	s = ' '+s.replace(PLEFT, ' '+PLEFT+' ')
	s = s.replace(PRIGHT, ' '+PRIGHT+' ')+' '
	token_list = list()
	regex = __merge_regex__()
	result = re.findall(regex, s)
	for entry in result:
		result = re.findall(regex, s)
		for (index, item) in enumerate(entry):
			if item != '':
				func = __regex__[index][1]
				token_list.append(func(item))
	if token_list[0] == PLEFT: 
		return __parse_exp__(token_list, 0)[0]
	else: # single element.
		return token_list[0]


def printExp(exp, depth = -1):
	iprint = lambda s, d:sys.stdout.write(''.join([' ' for i in range(d*4)])+str(s)+'\n')
	if not isinstance(exp, list):
		exp = [exp]
	for item in exp:
		if isinstance(item, list):
			printExp(item, depth+1)
		elif isinstance(item, Keyword):
			color.begin(color.blue)
			iprint(item, depth+(item != exp[0]))
			color.end()
		elif isinstance(item, Symbol):
			color.begin(color.green)
			iprint(item, depth+(item != exp[0]))
			color.end()
		elif isinstance(item, str):
			color.begin(color.red)
			iprint(item, depth+(item != exp[0]))
			color.end()
		elif isinstance(item, int) or isinstance(item, float):
			color.begin(color.magenta)
			iprint(item, depth+(item != exp[0]))
			color.end()
