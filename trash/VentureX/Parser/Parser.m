#import <XCTest/XCTest.h>
#import "Parser.h"

@interface Parser : XCTestCase

@end

@implementation Parser

- (void)setUp
{
    [super setUp];
}

- (void)tearDown
{
    [super tearDown];
}

- (void)testExample
{
    XCTFail(@"No implementation for \"%s\"", __PRETTY_FUNCTION__);
}

- (void)testBasicParsing {
	Parser *parser;
	parser.tokenize("abc");
}


@end
