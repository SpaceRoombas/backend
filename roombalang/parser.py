from roombalang.lexer import Token, TokenTypes, INFIX_OPS


class Node:
    def __init__(self, token, children=None):
        if children is None:
            children = []
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

        elif tokens[0].text == "while":
            return _parse_while(tokens)

        elif tokens[0].text == "for":
            return _parse_for(tokens)

        elif tokens[0].text == "let" or tokens[0].text == "fun":
            return _parse_declaration(tokens)

        elif tokens[0].text == "return":
            return Node(tokens.pop(0), [_parse_expression(tokens)])

        _error(tokens[0])

    if tokens[0].type == TokenTypes.IDENTIFIER:

        if tokens[1].type == TokenTypes.EQUALS:
            return _parse_declaration(tokens)

        if tokens[1].type in [TokenTypes.OPEN_PAREN, TokenTypes.OPEN_BRACKET, TokenTypes.INFIX_OP,
                              TokenTypes.POSTFIX_OP]:
            return _parse_expression(tokens)

        _error(tokens[0])

    if tokens[0].type == TokenTypes.OPEN_PAREN or tokens[0].type == TokenTypes.OPEN_BRACKET \
            or tokens[0].type == TokenTypes.PREFIX_OP or tokens[0].type == TokenTypes.LITERAL:
        return _parse_expression(tokens)

    # This MIGHT not work for adding a filler node, if it does then it's a bad solution
    return Node(Token(TokenTypes.SEMICOLON, ""))


def _is_statement(tokens):
    if tokens[0].type == TokenTypes.KEYWORD:

        if tokens[0].text == "if":
            return True

        if tokens[0].text == "while":
            return True

        if tokens[0].text == "for":
            return True

        if tokens[0].text == "let" or tokens[0].text == "fun":
            return True

        if tokens[0].text == "return":
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
    if len(tokens) > 0 and _is_statement(tokens):
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

    if len(tokens) > 0 and tokens[0].type == TokenTypes.KEYWORD and tokens[0].text == "else":
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
        root.children.append(_parse_statement(tokens))

    return root


def _parse_expression(tokens):

    def check_postfix(node):
        if len(tokens) > 0 and tokens[0].type == TokenTypes.POSTFIX_OP:
            return Node(tokens.pop(0), [node])
        else:
            return node

    end = len(tokens)
    infix = False
    depth = 0
    min_depth = float('inf')
    for idx, i in enumerate(tokens):

        if i.type in [TokenTypes.OPEN_PAREN, TokenTypes.OPEN_BRACKET]:
            depth += 1
        elif i.type in [TokenTypes.CLOSE_PAREN, TokenTypes.CLOSE_BRACKET]:
            depth -= 1
        elif depth < 0:
            end = idx-1
            break
        elif i.type == TokenTypes.INFIX_OP:
            infix = True
            if min_depth > depth:
                min_depth = depth
        elif i.type not in [TokenTypes.IDENTIFIER, TokenTypes.INFIX_OP, TokenTypes.PREFIX_OP,
                            TokenTypes.POSTFIX_OP, TokenTypes.COMMA, TokenTypes.LITERAL, TokenTypes.CLOSE_PAREN,
                            TokenTypes.OPEN_PAREN, TokenTypes.OPEN_BRACKET, TokenTypes.CLOSE_BRACKET]:
            end = idx
            break

    # parse math with infix ops
    if infix:
        # remove useless surrounding parenthesis if they're in there
        for _ in range(0, min_depth):
            tokens.pop(end-1)
            tokens.pop(0)
            end -= 2

        OP_PREC = INFIX_OPS.copy()
        OP_PREC.reverse() # we need to do order of operations backwards
        for op in OP_PREC:
            depth = 0
            for idx in range(0, end):
                if tokens[idx].type in [TokenTypes.OPEN_PAREN, TokenTypes.OPEN_BRACKET]:
                    depth += 1
                elif tokens[idx].type in [TokenTypes.CLOSE_PAREN, TokenTypes.CLOSE_BRACKET]:
                    depth -= 1
                elif depth == 0 and tokens[idx].type == TokenTypes.INFIX_OP and tokens[idx].text == op:
                    # split left and right side and parse
                    left = tokens[:idx]
                    right = tokens[idx+1:end]
                    op = tokens[idx]

                    # remove all parsed tokens in a way that will affect the original list
                    for _ in range(0, end):
                        tokens.pop(0)

                    return Node(op, [_parse_expression(left), _parse_expression(right)])
    # lists
    elif tokens[0].type == TokenTypes.OPEN_BRACKET:
        temp = tokens.pop(0)
        root = Node(temp)

        temp = tokens.pop(0)
        last_comma = True
        while temp.type != TokenTypes.CLOSE_BRACKET:
            if temp.type == TokenTypes.COMMA and not last_comma:
                last_comma = True

            elif last_comma:
                last_comma = False
                root.children.append(_parse_expression(tokens))

            else:
                _error(temp)

            temp = tokens.pop(0)

        return root

    # function calls / variables
    elif tokens[0].type == TokenTypes.IDENTIFIER:
        temp = tokens.pop(0)
        root = Node(temp)

        # if the last token is a variable we'll have to return it
        if len(tokens) == 0:
            return root

        if tokens[0].type == TokenTypes.OPEN_PAREN:
            # in this case the expression is a function call
            temp = tokens.pop(0)
            last_comma = True

            while temp.type != TokenTypes.CLOSE_PAREN:
                if temp.type == TokenTypes.COMMA and not last_comma:
                    last_comma = True

                elif temp.type != TokenTypes.COMMA and last_comma:
                    last_comma = False
                    root.children.append(_parse_expression(tokens))

                else:
                    _error(temp)

                temp = tokens.pop(0)

            while tokens[0].type == TokenTypes.OPEN_BRACKET:
                root.children.append(tokens.pop(0))
                root.children.append(_parse_expression(tokens))
                tokens.pop(0)

            return root

        elif tokens[0].type == TokenTypes.OPEN_BRACKET:
            while tokens[0].type == TokenTypes.OPEN_BRACKET:
                root.children.append(tokens.pop(0))
                root.children.append(_parse_expression(tokens))
                tokens.pop(0)

            return root

        else:
            # otherwise it's just a plain old variable
            return check_postfix(root)

    elif tokens[0].type == TokenTypes.LITERAL:
        return check_postfix(Node(tokens.pop(0)))

    elif tokens[0].type == TokenTypes.PREFIX_OP:
        return Node(tokens.pop(0), [_parse_expression(tokens)])

    # if we get down here we're either not in an expression or something very very bad has happened
    _error(tokens.pop(0))


def _parse_declaration(tokens):
    temp = tokens.pop(0)
    root = None

    if temp.type == TokenTypes.KEYWORD:
        if temp.text != "let" and temp.text != "fun":
            _error(temp)

        root = Node(temp)
        temp = tokens.pop(0)

    else:
        root = Node(Token(TokenTypes.KEYWORD, "let"))

    if temp.type != TokenTypes.IDENTIFIER:
        _error(temp)

    root.children.append(temp)

    temp = tokens.pop(0)
    if temp.type == TokenTypes.EQUALS:
        root.children.append(_parse_expression(tokens))
        return root

    elif temp.type == TokenTypes.OPEN_PAREN:

        root.children.append(temp)
        last_comma = True
        temp = tokens.pop(0)
        while temp.type != TokenTypes.CLOSE_PAREN:

            if temp.type == TokenTypes.COMMA and not last_comma:
                last_comma = True
            elif temp.type == TokenTypes.IDENTIFIER and last_comma:
                root.children.append(temp)
                last_comma = False
            else:
                _error(temp)

            temp = tokens.pop(0)

        root.children.append(temp)

        temp = tokens.pop(0)
        if temp.type != TokenTypes.OPEN_BRACE:
            _error(temp)

        root.children += _parse_statements(tokens)

        return root

    else:
        _error(temp)
