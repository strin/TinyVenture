#include "Exception.h"
#include "Type.h"

using namespace VentureX;
using namespace std;

size_t Exception::error_counter = 0;

Exception::Exception() {
	this->message = "error #"+to_string(error_counter++)+": oops.. some goes wrong.";
}

Exception::Exception(string _message) {
	this->message = "error #"+to_string(error_counter++)+": "+_message;
}

Exception::Exception(string _message, TokenLocation _loc) {
	this->message = "error #"+to_string(error_counter++)+": "+_message;
	this->loc = _loc;
}

string Exception::getMessage() {
	return message;
}
void Exception::reset_counter() {
	error_counter = 0;
}

TypeException::TypeException()
: Exception() {
	
}

TypeException::TypeException(string _message)
: Exception(_message) {
	
}

TypeException::TypeException(string _message, TokenLocation _loc)
: Exception(_message, _loc) {
	
}