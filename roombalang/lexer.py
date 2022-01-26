from enum import Enum, auto

KEYWORDS = ['let', 'if', 'while', 'for', 'fun', 'return']
INFIX_OPS = ['+', '-', '*', '**', '/', '\\', '%', '&&', '||', '^', '==', '>=', '<=', '!=']
POSTFIX_OPS = ['++', '--']
PREFIX_OPS = ['!']
SPECIAL_CHARS = '!=<>?%^\\/+-&,;'
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
    ERROR = auto()


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
        return []

    token = ''
    is_string = False

    for idx, c in enumerate(list(text)):

        if len(token) == 0 and c.isspace():
            continue

        if len(token) != 0:
            if c in SPECIAL_CHARS and token[-1] in SPECIAL_CHARS:
                return accept()

            if c in SPECIAL_CHARS != token[-1] in SPECIAL_CHARS:
                return accept()

            if c in PAIRED_CHARS or token[-1] in PAIRED_CHARS:
                return accept()

            if c.isspace():
                return accept()

        token += c

    return []
