#ifndef __VentureX__Token__
#define __VentureX__Token__

#include <iostream>
#include <vector>
#include <string>

namespace  VentureX {
	enum TokenType {TOKEN_NUMERIC, TOKEN_STR, TOKEN_PLEFT, TOKEN_PRIGHT, TOKEN_VAR, TOKEN_LAMBDA, TOKEN_IF,
		TOKEN_OR, TOKEN_AND, TOKEN_PLUS, TOKEN_MINUS, TOKEN_FLIP, TOKEN_TRUE, TOKEN_FALSE};
	const std::string PLEFT = "[";
	const std::string PRIGHT = "]";
	const std::string STR_TRUE = "true";
	const std::string STR_FALSE = "false";
	
	static const std::vector<std::pair<TokenType, std::string>> token_regex
													= {	{TOKEN_PLEFT, "\\"+PLEFT},
														{TOKEN_PRIGHT, "\\"+PRIGHT},
														{TOKEN_NUMERIC, "[0-9]+\\.?[0-9]* "},
														{TOKEN_NUMERIC, "[0-9]*\\.?[0-9]+ "},
														{TOKEN_LAMBDA, "lambda"},
														{TOKEN_IF, "if"},
														{TOKEN_OR, "or"},
														{TOKEN_TRUE, STR_TRUE},
														{TOKEN_FALSE, STR_FALSE},
														{TOKEN_AND, "and"},
														{TOKEN_PLUS, "\\+"},
														{TOKEN_MINUS, "\\-"},
														{TOKEN_FLIP, "flip"},
														{TOKEN_STR, "'[A-Za-z_][A-Za-z_0-9]*"},
														{TOKEN_VAR, "[A-Za-z_][A-Za-z_0-9]*"}
													};

	class TokenLocation {
	public:
		TokenLocation() {
			row = -1; col = -1;
		}
		TokenLocation(int _row, int _col) {
			row = _row; col = _col;
		}
		int row, col;
	};

	class Token {
	public:
		Token(std::string _str, const TokenType _type)
		:str(_str), type(_type){
			
		}
		std::string str;
		const TokenType type;
		TokenLocation loc;
	};
}

#endif
