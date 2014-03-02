#ifndef __VentureX__Exception__
#define __VentureX__Exception__

#include <iostream>
#include <string>
#include "Token.h"
#include "Type.h"

namespace VentureX {
	
	class Exception {
	public:
		Exception();
		Exception(std::string _message);
		Exception(std::string _message, TokenLocation _loc);
		std::string getMessage();
		static void reset_counter();
	private:
		std::string message;
		TokenLocation loc;
		static size_t error_counter;
	};
	
	class TypeException : public Exception {
	public:
		TypeException();
		TypeException(std::string _message);
		TypeException(std::string _message, TokenLocation _loc);
	};
}
#endif /* defined(__VentureX__Exception__) */
