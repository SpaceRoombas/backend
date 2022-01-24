import pytest
from roombalang.lexer import tokenize, TokenTypes


def test_function_declaration():
    tokens = tokenize("fun taco(a, b){return 6}", 42)
    assert tokens[0].type == TokenTypes.KEYWORD
    assert tokens[0].text == "fun"
    assert tokens[1].type == TokenTypes.IDENTIFIER
    assert tokens[1].text == "taco"
    assert tokens[2].type == TokenTypes.OPEN_PAREN
    assert tokens[2].text == "("
    assert tokens[3].type == TokenTypes.IDENTIFIER
    assert tokens[3].text == "a"
    assert tokens[4].type == TokenTypes.COMMA
    assert tokens[4].text == ","
    assert tokens[5].type == TokenTypes.IDENTIFIER
    assert tokens[5].text == "b"
    assert tokens[6].type == TokenTypes.CLOSE_PAREN
    assert tokens[6].text == ")"
    assert tokens[7].type == TokenTypes.OPEN_BRACE
    assert tokens[7].text == "{"
    assert tokens[8].type == TokenTypes.KEYWORD
    assert tokens[8].text == "return"
    assert tokens[9].type == TokenTypes.LITERAL
    assert tokens[9].text == "6"
    assert tokens[10].type == TokenTypes.CLOSE_BRACE
    assert tokens[10].text == "}"
    assert tokens[10].line == 42

def test_math():
    tokens = tokenize("(2+!a+b++-7)/42*6", 12)
    assert tokens[0].type == TokenTypes.OPEN_PAREN
    assert tokens[0].text == "("
    assert tokens[1].type == TokenTypes.LITERAL
    assert tokens[1].text == "2"
    assert tokens[2].type == TokenTypes.INFIX_OP
    assert tokens[2].text == "+"
    assert tokens[3].type == TokenTypes.PREFIX_OP
    assert tokens[3].text == "!"
    assert tokens[4].type == TokenTypes.IDENTIFIER
    assert tokens[4].text == "a"
    assert tokens[5].type == TokenTypes.INFIX_OP
    assert tokens[5].text == "+"
    assert tokens[6].type == TokenTypes.IDENTIFIER
    assert tokens[6].text == "b"
    assert tokens[7].type == TokenTypes.POSTFIX_OP
    assert tokens[7].text == "++"
    assert tokens[8].type == TokenTypes.INFIX_OP
    assert tokens[8].text == "-"
    assert tokens[9].type == TokenTypes.LITERAL
    assert tokens[9].text == "7"
    assert tokens[10].type == TokenTypes.CLOSE_PAREN
    assert tokens[10].text == ")"
    assert tokens[11].type == TokenTypes.INFIX_OP
    assert tokens[11].text == "/"
    assert tokens[12].type == TokenTypes.LITERAL
    assert tokens[12].text == "42"
    assert tokens[13].type == TokenTypes.INFIX_OP
    assert tokens[13].text == "*"
    assert tokens[14].type == TokenTypes.LITERAL
    assert tokens[14].text == "6"

