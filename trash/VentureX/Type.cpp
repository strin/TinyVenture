#include "Type.h"
#include "Exception.h"
#include "boost/algorithm/string.hpp"

#define IS_NUMBER(x) ((x) <= '9' && (x) >= '0')
#define CH_TO_NUM(x) ((x)-'0')

using namespace VentureX;
using namespace std;

TypeInt::TypeInt() {
	this->type = LITERAL_INT;
}

TypeInt::~TypeInt() {
}

TypeFloat::TypeFloat() {
	this->type = LITERAL_FLOAT;
}

TypeFloat::~TypeFloat() {
	
}

TypeString::TypeString() {
	this->type = LITERAL_STR;
}

TypeString::~TypeString() {
	
}

TypeBool::TypeBool() {
	this->type = LITERAL_BOOL;
}

TypeBool::~TypeBool() {
	
}

void TypeInt::parseToken(const VentureX::Token &t) {
	v = 0;
	string token_str = t.str;
	boost::replace_all(token_str, " ", "");
	for(auto it = token_str.begin(); it != token_str.end(); it++) {
		if(!IS_NUMBER(*it))
			throw TypeException("token is not an integer literal.");
		v = v*10+CH_TO_NUM(*it);
	}
}

void TypeBool::parseToken(const VentureX::Token &t) {
	string token_str = t.str;
	boost::replace_all(token_str, " ", "");
	if(token_str == STR_TRUE) {
		v = true;
	}else if(token_str == STR_FALSE) {
		v = false;
	}else{
		throw TypeException("token is not a bool literal.", t.loc);
	}
}

void TypeFloat::parseToken(const VentureX::Token &t) {
	string token_str = t.str;
	boost::replace_all(token_str, " ", "");
	vector<string> strs;
	boost::split(strs,token_str,boost::is_any_of("."));
	try {
		if(strs.size() > 2)
			throw TypeException();
		v = 0;
		if(strs[0].length() > 0)
			for(auto it = strs[0].begin(); it != strs[0].end(); it++) {
				if(!IS_NUMBER(*it))
					throw TypeException();
				v = v*10+CH_TO_NUM(*it);
			}
		double frac = 0;
		if(strs.size() > 1 && strs[1].length() > 0)
			for(auto it = strs[1].end()-1; it != strs[1].begin()-1; it--) {
				if(!IS_NUMBER(*it))
					throw TypeException();
				frac = (frac+CH_TO_NUM(*it))/10.0;
			}
		v += frac;
	}catch(TypeException ee) {
		throw TypeException("token is not a float literal.");
	}
}

void TypeString::parseToken(const VentureX::Token &t) {
	this->v = t.str;
	boost::replace_all(this->v, " ", "");
}

