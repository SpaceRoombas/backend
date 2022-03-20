from roombalang.parser import Parser
from transpiler import Transpiler
from interpreter import Interpreter

if __name__ == "__main__":
    parser = Parser()
    transpiler = Transpiler()
    fns = {"print": (lambda val: print(val[0]), 1)}

    code = input("input code to run:\n")

    interpreter = Interpreter(code, fns, parser, transpiler)

    interpreter.eval()
