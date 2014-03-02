#include "Parser.h"
#include "boost/algorithm/string.hpp"
#include "boost/regex.hpp"
#include "Type.h"
#include "Token.h"

using namespace VentureX;
using namespace std;

void Parser::tokenize(std::string exp, std::vector<Token*>& tokens) {
	boost::replace_all(exp, PLEFT, " "+PLEFT+" ");
	boost::replace_all(exp, PRIGHT, " "+PRIGHT+" ");
	/* build rule */
	std::string rule_str = "";
	for(auto& regex : token_regex) {
		rule_str += "("+regex.second+")|";
	}
	cout << rule_str << endl;
	rule_str = rule_str.substr(0, rule_str.length()-1);
	boost::regex rule(rule_str);
	/* tokenize strings using regex exp */
	boost::match_results<std::string::const_iterator> what;
	std::string::const_iterator start = exp.begin(), end = exp.end();
	while(boost::regex_search(start, end, what, rule)) {
		for(int i = 1; i < token_regex.size(); i++) {
			if(what[i].matched) {
				tokens.push_back(new Token(string(what[i].first, what[i].second), token_regex[i-1].first));
				break;
			}
		}
		start = what[0].second;
	}
	for(auto token : tokens) {
		printf("%s %d\n", token->str.c_str(), token->type);
		fflush(stdout);
	}
}

void Parser::freetokens(std::vector<Token*>& tokens) {
	for(auto* token : tokens)
		delete token;
	tokens.clear();
}

Type* Parser::compute(const std::vector<Token*>& tokens, int depth) {
	if(depth == 0) {
		this->p_token = 0;
	}
	Token* op = tokens[++p_token];
	vector<Type*> arglist;
	vector<Token*> argTokens;
	p_token++;
	while(tokens[p_token]->type != TOKEN_PRIGHT) {
		if(tokens[p_token]->type == TOKEN_PLEFT) { // recursive computing.
			arglist.push_back(this->compute(tokens, depth+1));
			argTokens.push_back(0);
		}else{									   // atom.
			arglist.push_back(0);
			argTokens.push_back(tokens[p_token]);
//			TypeRawToken* t = new TypeRawToken();
//			t->parseToken(*tokens[p_token]);
//			arglist.push_back(t);
		}
		p_token++;
		printf("%s\n", tokens[p_token]->str.c_str());
	}
	Type* ret = nullptr;
	if(op->type == TOKEN_PLUS) {
		if(arglist.size() == 0)
			throw Exception();
		TypeFloat* res = new TypeFloat();
		res->v = 0;
		for(int i = 0; i < arglist.size(); i++) {
			if(arglist[i] != nullptr) {
				if(arglist[i]->type == LITERAL_FLOAT) {
					res->v += ((TypeFloat*)arglist[i])->v;
				}else
					throw Exception();
			}
			if(argTokens[i] != nullptr) {
				TypeFloat temp;
				temp.parseToken(*argTokens[i]);
				res->v += temp.v;
			}
		}
		ret = res;
	}
	for(auto* type : arglist) {
		delete type;
	}
	arglist.clear();
	return ret;
}