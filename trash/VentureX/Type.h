#ifndef __VentureX__Type__
#define __VentureX__Type__

#include <iostream>
#include <string>
#include <vector>

#include "Exception.h"
#include "Token.h"

namespace VentureX {
	
	enum PrimitiveType {LITERAL_STR, LITERAL_INT, LITERAL_BOOL, LITERAL_FLOAT, TYPE_FUNC};
	
	class Type {
	public:
//		virtual ~Type() = 0;
		virtual void parseToken(const Token& t) = 0;
		PrimitiveType type;
	};
	
	class TypeInt : public Type {
	public:
		TypeInt();
		~TypeInt();
		int v;
		void parseToken(const Token& t);
	};
	
	class TypeFloat : public Type {
	public:
		TypeFloat();
		~TypeFloat();
		double v;
		void parseToken(const Token& t);
	};
	
	class TypeBool : public Type {
	public:
		TypeBool();
		~TypeBool();
		bool v;
		void parseToken(const Token& t);
	};
	
	class TypeString : public Type {
	public:
		TypeString();
		~TypeString();
		std::string v;
		void parseToken(const Token& t);
	};
	
//	class TypeRawToken : public Type {
//	public:
//		const Token* v;
//		void parseToken(const Token& t);
//	};
}

#endif /* defined(__VentureX__Type__) */
