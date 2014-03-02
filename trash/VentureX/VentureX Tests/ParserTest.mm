//
//  ParserTest.mm
//  VentureX
//
//  Created by Tianlin Shi on 2/11/14.
//  Copyright (c) 2014 Tianlin Shi. All rights reserved.
//

#import <XCTest/XCTest.h>
#import "Parser.h"

@interface ParserTest : XCTestCase

@end

@implementation ParserTest

- (void)setUp
{
    [super setUp];
    // Put setup code here. This method is called before the invocation of each test method in the class.
}

- (void)tearDown
{
    // Put teardown code here. This method is called after the invocation of each test method in the class.
    [super tearDown];
}

- (void)testExample
{
	VectureX::Parser* parser;
	std::vector<std::string> result;
	parser->tokenize("hello", result);
	for(auto& x : result) {
		std::cout << x << " ";
	}
	std::cout << std::endl;
}

@end
