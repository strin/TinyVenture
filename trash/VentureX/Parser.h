#ifndef __VentureX__Parser__
#define __VentureX__Parser__

#include <iostream>
#include <vector>
#include <string>

#include "Type.h"

namespace VentureX {
	class Parser {
	public:
		/* tokenize a venture expression */
		void tokenize(std::string exp, std::vector<Token*>& tokens);
		
		/* compute a venture expression */
		Type* compute(const std::vector<Token*>& tokens, int depth = 0);
		
		/* free a tokenized sequence */
		void freetokens(std::vector<Token*>& tokens);
		
	private:
		int p_token;
	};
}
#endif
