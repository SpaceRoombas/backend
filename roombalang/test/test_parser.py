import pytest
from roombalang.lexer import tokenize
from roombalang.parser import parse_file


def test_function_declaration():
    tokens = tokenize("fun taco(a, b){return 6}", 42)
    tree = parse_file(tokens)
    print(tree)


def test_math():
    tokens = tokenize("(2+!a+b++-7)/42*6", 12)
    tree = parse_file(tokens)
    print(tree)


def test_more_complicated_function():
    tokens = tokenize("fun nice(){for(let i=7;i<=2;i--){print(\"69fourtwenty\")return 420}}", 7)
    tree = parse_file(tokens)
    print(tree)

def test_if():
    tokens = tokenize("if(a==b){print(\"woo stuff\")}", 7)
    tree = parse_file(tokens)
    print(tree)

def test_while():
    tokens = tokenize("while(taco--){move(LEFT)}", 7)
    tree = parse_file(tokens)
    print(tree)