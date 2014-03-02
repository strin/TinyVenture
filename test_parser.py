import parser
import re

def test_regex():
	regex = parser.__merge_regex__()
	print regex
	m = re.findall(regex, '[ + 1.3 .3 3. 134 ] ')
	print m
	m = re.findall(regex, '[ lambda hello x + y ] ')
	print m
	return True

def test_parse():
	parser.printExp(parser.parse('[+ [lambda 1 2] 3.2 43 .32 [/ 16 3]]'))
	parser.printExp(parser.parse("[+ [* 'b a] 3.2 43 .32 [/ 16 3]]"))

test_cases = [ 
			  # test_regex,
			  test_parse
			 ]

def test_all():
	for case in test_cases:
		print
		if case() == False:
			print '- Test Failed : '+str(case)
			return False
	print
	print '- All Test Passed.'
	return True

test_all()

