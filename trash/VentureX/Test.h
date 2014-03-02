#ifndef __VentureX__Test__
#define __VentureX__Test__

#include <iostream>

#include "Type.h"
#include "Exception.h"

using namespace VentureX;
using namespace std;

bool testPrimitiveType() {
	Parser parser;
	std::vector<Token*> tks;
	string test = "[+ 1.23 .31 32.43 1. 1 324]";
	parser.tokenize(test, tks);
	double groundtruth[] = {0, 0, 1.23, .31, 32.43, 1., 1, 324};
	for(int i = 2; i < tks.size()-1; i++) {
		TypeFloat tf;
		try{
			tf.parseToken(*tks[i]);
		}catch(TypeException ee) {
			printf("%s\n", ee.getMessage().c_str());
			return false;
		}
		if(tf.v != groundtruth[i]) {
			printf("test fail: %lf != %lf\n", tf.v, groundtruth[i]);
			return false;
		}
	}
	parser.freetokens(tks);
	
	test = "[or true false]";
	parser.tokenize(test, tks);
	double groundtruth2[] = {0, 0, true, false};
	for(int i = 2; i < tks.size()-1; i++) {
		TypeBool tb;
		try{
			tb.parseToken(*tks[i]);
		}catch(TypeException ee) {
			printf("%s\n", ee.getMessage().c_str());
			return false;
		}
		if(tb.v != groundtruth2[i]) {
			printf("test fail: %d != %d\n", tb.v, groundtruth2[i]);
			return false;
		}
	}
	parser.freetokens(tks);
	return true;
}

bool testArithmeticsSimple() {
	Parser parser;
	std::vector<Token*> tks;
	string test = "[+ 1.23 .31 [+ 32.43 1. 1 324]]";
	parser.tokenize(test, tks);
	double groundtruth[] = {0, 0, 1.23, .31, 32.43, 1., 1, 324};
	double gt = 0;
	for(auto x : groundtruth) {
		gt += x;
	}
	Type* res = parser.compute(tks);
	parser.freetokens(tks);
	if(res->type == LITERAL_FLOAT && ((TypeFloat*)res)->v == gt) {
		return true;
	}
	return false;
}

bool (*regTest[])() = {
//	testPrimitiveType,
	testArithmeticsSimple
};

bool testAll() {
	for(auto func : regTest) {
		if(!(*func)()) {
			printf("FAILED.\n");
			return false;
		}
	}
	printf("ALL TEST PASSED.\n");
	return true;
}

#endif /* defined(__VentureX__Test__) */
