from enum import Enum, auto

KEYWORDS = ['let', 'if', 'while', 'for', 'fun']
INFIX_OPS = ['+', '-', '*', '**', '/', '\\', '%', '&&', '||', '^', '==', '>=', '<=', '!=']
POSTFIX_OPS = ['++', '--']
PREFIX_OPS = ['!']
PAIRED_CHARS = '(){}[]'


class TokenTypes(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INFIX_OP = auto()
    PREFIX_OP = auto()
    POSTFIX_OP = auto()
    LITERAL = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
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
        elif text == '(':
            self.type = TokenTypes.OPEN_PAREN
        elif text == ')':
            self.type = TokenTypes.CLOSE_PAREN
        elif text == '[':
            self.type = TokenTypes.OPEN_BRACKET
        elif text == ']':
            self.type = TokenTypes.CLOSE_BRACKET
        elif text == '{':
            self.type = TokenTypes.OPEN_BRACE
        elif text == '}':
            self.type = TokenTypes.CLOSE_BRACE
        else:
            self.type = TokenTypes.ERROR


def tokenize(text, line):
    if len(text) == 0:
        return []

    token = ''
    is_string = False
    for idx, c in enumerate(list(text)):
        if idx == 0 and (c == '\"' or c == '\''):
            is_string = True
            token += c
        elif is_string:
            if (c == '\"' or c == '\'') and token[-1] != '\\':
                token += c
                return [Token(token, line)] + tokenize(text[idx + 1:], line)
            else:
                token += c
        elif idx == 0 or (token[-1].isalnum() == c.isalnum() and token[-1].isspace() == c.isspace()):
            if c in PAIRED_CHARS:
                if idx == 0:
                    token += c
                    return [Token(token, line)] + tokenize(text[idx + 1:], line)
                else:
                    return [Token(token, line)] + tokenize(text[idx:], line)
            else:
                token += c
        else:
            return [Token(token, line)] + tokenize(text[idx:], line)
