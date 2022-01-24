import pytest
from roombalang.lexer import tokenize, TokenTypes


def test_tokenization():
    tokens = tokenize("fun taco(a, b){return 6}", 1)
    assert tokens[0].type == TokenTypes.KEYWORD
    assert tokens[0].text == "fun"
    assert tokens[1].type == TokenTypes.IDENTIFIER
    assert tokens[1].text == "taco"
    assert tokens[2].type == TokenTypes.SYNTAX
    assert tokens[2].text == "("
    assert tokens[3].type == TokenTypes.IDENTIFIER
    assert tokens[3].text == "a"
    assert tokens[4].type == TokenTypes.SYNTAX
    assert tokens[4].text == ","
    assert tokens[5].type == TokenTypes.IDENTIFIER
    assert tokens[5].text == "b"
    assert tokens[6].type == TokenTypes.SYNTAX
    assert tokens[6].text == ")"
    assert tokens[7].type == TokenTypes.SYNTAX
    assert tokens[7].text == "{"
    assert tokens[8].type == TokenTypes.KEYWORD
    assert tokens[8].text == "return"
    assert tokens[9].type == TokenTypes.LITERAL
    assert tokens[9].text == "6"
    assert tokens[10].type == TokenTypes.SYNTAX
    assert tokens[10].text == "}"
