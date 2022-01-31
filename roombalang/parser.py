from lexer import Token, TokenTypes

class Node:
    def __init__(self, token, children=[]):
        self.token = token
        self.children = children

def parse_file(tokens):
    if tokens[-1].type == TokenTypes.EOF:
        return Node(tokens.pop(), _parse_statements(tokens))
    else:
        raise Exception("File does not end with EOF")

def _error(token):
    raise Exception(f'Syntax Error: {token.line} token {token.text}')

def _parse_statement(tokens):
    if tokens[0].type == TokenTypes.KEYWORD:

        if tokens[0].text == "if":
            return _parse_if(tokens)

        if tokens[0].text == "while":
            return _parse_while(tokens)

        if tokens[0].text == "for":
            return _parse_for(tokens)

        if tokens[0].text == "let" or tokens[0].text == "fun":
            return _parse_declaration(tokens)

        _error(tokens[0])

    if tokens[0].type == TokenTypes.IDENTIFIER:

        if tokens[1].type == TokenTypes.EQUALS:
            return _parse_declaration(tokens)

        if tokens[1].type == TokenTypes.OPEN_PAREN or tokens[1].type == TokenTypes.OPEN_BRACKET:
            return _parse_expression(tokens)

        _error(tokens[0])

    if tokens[0].type == TokenTypes.OPEN_PAREN or tokens[0].type == TokenTypes.OPEN_BRACKET\
        or tokens[0].type == TokenTypes.PREFIX_OP or tokens[0].type == TokenTypes.LITERAL:

        return _parse_expression(tokens)

    #This MIGHT not work for adding a filler node, if it does then it's a bad solution
    return Node(Token(TokenTypes.SEMICOLON, ""))


def _is_statement(tokens):
    if tokens[0].type == TokenTypes.KEYWORD:

        if tokens[0].text == "if":
            return True

        if tokens[0].text == "while" :
            return True

        if tokens[0].text == "for":
            return True

        if tokens[0].text == "let" or tokens[0].text == "fun":
            return True

        return False

    if tokens[0].type == TokenTypes.IDENTIFIER:

        if tokens[1].type == TokenTypes.EQUALS:
            return True

        if tokens[1].type == TokenTypes.OPEN_PAREN or tokens[1].type == TokenTypes.OPEN_BRACKET:
            return True

        return False

    if tokens[0].type == TokenTypes.OPEN_PAREN or tokens[0].type == TokenTypes.OPEN_BRACKET \
            or tokens[0].type == TokenTypes.PREFIX_OP or tokens[0].type == TokenTypes.LITERAL:

        return True

    return False


def _parse_statements(tokens):
    if _is_statement(tokens):
        return [_parse_statement(tokens)] + _parse_statements(tokens)
    else:
        return []


def _parse_if(tokens):
    root = Node(tokens.pop(0))

    temp = tokens.pop(0)
    if temp.type != TokenTypes.OPEN_PAREN:
        _error(temp)

    root.children.append(_parse_expression(tokens))

    temp = tokens.pop(0)
    if temp.type != TokenTypes.CLOSE_PAREN:
        _error(temp)

    temp = tokens.pop(0)
    if temp.type == TokenTypes.OPEN_BRACE:
        root.children += _parse_statements(tokens)

        temp = tokens.pop(0)
        if temp.type != TokenTypes.CLOSE_BRACE:
            _error(temp)

    else:
        root.children += _parse_statement(tokens)


    if tokens[0].type == TokenTypes.KEYWORD and tokens[0].text == "else":
        tokens.pop(0)

        temp = tokens.pop(0)
        if temp.type == TokenTypes.OPEN_BRACE:
            root.children += _parse_statements(tokens)

            temp = tokens.pop(0)
            if temp.type != TokenTypes.CLOSE_BRACE:
                _error(temp)

        else:
            root.children += _parse_statement(tokens)

    return root


def _parse_while(tokens):
    root = Node(tokens.pop(0))

    temp = tokens.pop(0)
    if temp.type != TokenTypes.OPEN_PAREN:
        _error(temp)

    root.children.append(_parse_expression(tokens))

    temp = tokens.pop(0)
    if temp.type != TokenTypes.CLOSE_PAREN:
        _error(temp)

    temp = tokens.pop(0)
    if temp.type == TokenTypes.OPEN_BRACE:
        root.children += _parse_statements(tokens)

        temp = tokens.pop(0)
        if temp.type != TokenTypes.CLOSE_BRACE:
            _error(temp)

    else:
        root.children += _parse_statement(tokens)


    return root

def _parse_for(tokens):
    root = Node(tokens.pop(0))

    temp = tokens.pop(0)
    if temp.type != TokenTypes.OPEN_PAREN:
        _error(temp)

    root.children.append(_parse_declaration(tokens))
    temp = tokens.pop(0)
    if temp.type != TokenTypes.SEMICOLON:
        _error(temp)

    root.children.append(_parse_expression(tokens))
    temp = tokens.pop(0)
    if temp.type != TokenTypes.SEMICOLON:
        _error(temp)

    root.children.append(_parse_statement(tokens))

    temp = tokens.pop(0)
    if temp.type != TokenTypes.CLOSE_PAREN:
        _error(temp)

    temp = tokens.pop(0)
    if temp.type == TokenTypes.OPEN_BRACE:
        root.children += _parse_statements(tokens)

        temp = tokens.pop(0)
        if temp.type != TokenTypes.CLOSE_BRACE:
            _error(temp)

    else:
        root.children += _parse_statement(tokens)

    return root

def _parse_expression(tokens):


def _parse_declaration(tokens):

