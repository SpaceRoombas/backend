from enum import Enum, auto

KEYWORDS = ['let', 'if', 'while', 'for', 'fun', 'return']
# infix ops are ordered for precedence, do not change to be otherwise
INFIX_OPS = ['**', '*', '/', '\\', '%', '+', '-', '&&', '||', '^', '==', '<', '>' '>=', '<=', '!=', "*=",
             "/=", "\\=", "%=", "+=", "-=", "&=", "|=", "^="]
POSTFIX_OPS = ['++', '--']
PREFIX_OPS = ['!']
OPS = INFIX_OPS+POSTFIX_OPS+PREFIX_OPS
SPECIAL_CHARS = '!=<>?%^\\*/+-&,;'
PAIRED_CHARS = '(){}[]'


class TokenTypes(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INFIX_OP = auto()
    PREFIX_OP = auto()
    POSTFIX_OP = auto()
    LITERAL = auto()
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()
    EQUALS = auto()
    EOF = auto()


class Token:
    def __init__(self, text, line):
        self.text = text
        self.line = line

        if text in KEYWORDS:
            self.type = TokenTypes.KEYWORD
        elif text in INFIX_OPS:
            self.type = TokenTypes.INFIX_OP
        elif text in POSTFIX_OPS:
            self.type = TokenTypes.POSTFIX_OP
        elif text in PREFIX_OPS:
            self.type = TokenTypes.PREFIX_OP
        elif ((text[0] == "\"" or text[0] == "\'") and (text[-1] == "\"" or text[-1] == "\'")) \
                or text.replace('.', '', 1).isdigit():
            self.type = TokenTypes.LITERAL
        elif text == "EOF":
            self.type = TokenTypes.EOF
        elif text.isalnum():
            self.type = TokenTypes.IDENTIFIER
        elif text == "(":
            self.type = TokenTypes.OPEN_PAREN
        elif text == ")":
            self.type = TokenTypes.CLOSE_PAREN
        elif text == "[":
            self.type = TokenTypes.OPEN_BRACKET
        elif text == "]":
            self.type = TokenTypes.CLOSE_BRACKET
        elif text == "{":
            self.type = TokenTypes.OPEN_BRACE
        elif text == "}":
            self.type = TokenTypes.CLOSE_BRACE
        elif text == ",":
            self.type = TokenTypes.COMMA
        elif text == ";":
            self.type = TokenTypes.SEMICOLON
        elif text == "=":
            self.type = TokenTypes.EQUALS
        else:
            self.type = TokenTypes.ERROR


def tokenize(text, line):

    def accept(offset=0):
        return [Token(token, line)] + tokenize(text[idx+offset:], line)

    if len(text) == 0:
        return [Token("EOF", line)]

    token = ''
    is_string = False

    # the lexer has 7 rules:
    # 1. if the first character of a token is whitespace, discard it
    # 2. if the last 2 characters of a token are special characters then end the token
    # 3. if one but not both of the last two characters of a token are special characters then end the token
    # 4. if the next or last character of a token are special characters then end the token
    # 5. if the next character of a token is a special character and the concatenation of the last and next are not an
    #   op then end the token
    # 6. if the next character of a token is whitespace and the first character was not a quote then end the token
    # 7. if there is no more text remaining then end the token

    for idx, c in enumerate(list(text)):

        if len(token) == 0 and c.isspace():
            continue

        if len(token) != 0:
            if len(token) > 1 and token[-2] in SPECIAL_CHARS and token[-1] in SPECIAL_CHARS:
                return accept()

            if (c in SPECIAL_CHARS) != (token[-1] in SPECIAL_CHARS):
                return accept()

            if c in PAIRED_CHARS or token[-1] in PAIRED_CHARS:
                return accept()

            if c in SPECIAL_CHARS and not (token[-1] + c) in OPS:
                return accept()
              
            if c.isspace() and token[0] not in ['"', '\'']:
                return accept()

        token += c

    return [Token(token, line), Token("EOF", line)]
