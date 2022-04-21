from .vm import VM


class Interpreter:
    def __init__(self, code, functions, parser, transpiler):
        self._tree = parser.parse(code)
        self.bytecode = []
        self.vm = VM(functions)
        self._bytecode = transpiler.transpile(self._tree)
        self._done = False

    # evaluates all code in interpreter
    def eval(self):
        while not self._done:
            self.tick()

    # evaluates a single node of the ast
    def tick(self):
        ptr = self.vm.tick(self._bytecode)
        if ptr == -1:
            self._done = True

    def set_fns(self, fns):
        self.vm.external_fns = fns
