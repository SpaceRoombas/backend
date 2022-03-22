from lark import Lark

grammar = '''
start: _stmt*

_stmt: dec
      | _exp
      | ctrl
      | block
      | return
      | selfmath

?selfmath: iden "+=" math_exp -> selfadd
         | iden "-=" math_exp -> selfsub
         | iden "*=" math_exp -> selfmul
         | iden "/=" math_exp -> selfdiv
         | iden "%=" math_exp -> selfrem
         | iden "&=" math_exp -> selfand
         | iden "|=" math_exp -> selfor
         | iden "^=" math_exp -> selfxor

return: "return" _exp
block: "{" _stmt* "}"

ctrl: "if" "(" _exp ")" _stmt ["else" _stmt]       -> if
      | "while" "(" _exp ")" _stmt                 -> while
      | "for" "(" dec ";" _exp ";" _stmt ")" _stmt -> for

dec: ["let"] (iden | list_index) "=" _exp -> var_dec
    | "fun" iden "("[iden ("," iden)*] ")" _stmt -> fun_dec

_exp: lambda
    | math_exp
    | "("_exp")"

lambda: "("[iden ("," iden)*] ")" "=>" "{"_stmt"}"

?math_exp: sum
        | math_exp "!=" sum -> neq
        | math_exp "==" sum -> eq
        | math_exp ">=" sum -> meq
        | math_exp "<=" sum -> leq
        | math_exp ">"  sum -> mt
        | math_exp "<"  sum -> lt
        | math_exp "&&" sum -> and
        | math_exp "||" sum -> or
        | math_exp "^"  sum -> xor

?sum: product
    | sum "-" product -> sub
    | sum "+" product -> add

?product: power
        | product "/"  power -> div
        | product "%"  power -> rem
        | product "//" power -> idiv
        | product "*"  power -> mul

?power: prefixexp
      | power "**" prefixexp -> pow

?prefixexp: postfixexp
          | "!" prefixexp -> not
          | "-" prefixexp -> neg

?postfixexp: atom
           | postfixexp "++" -> inc
           | postfixexp "--" -> dec

?atom: lit
     | fun_call
     | list
     | list_index
     | iden
     | "(" math_exp ")"

lit: NUMBER
   | STRING
list_index: atom "[" _exp "]"
list: "[" _exp? [("," _exp)]* "]"
fun_call: atom "(" [_exp ("," _exp)*] ")"

iden: /[^\W\d]\w*/

%import common.ESCAPED_STRING -> STRING
%import common.NUMBER  -> NUMBER

%ignore /[ \t\f\r]+/
'''


class Parser:
    def __init__(self):
        self._parser = Lark(grammar, parser='lalr', debug=True)

    def parse(self, code):
        return self._parser.parse(code)
