class Transpiler:
    SELFFIX = ['selfdiv', 'selfmul', 'selfadd', 'selfsub', 'selfrem', 'selfxor', 'selfor', 'selfand']
    INFIX = ['div', 'mul', 'add', 'sub', 'idiv', 'rem', 'xor', 'or', 'and', 'exp', 'leq', 'meq', 'eq', 'lt', 'mt',
             'neq']
    PREFIX = ['not', 'neg']

    def __init__(self):
        self._highest_label = 0

    def _get_label(self):
        self._highest_label += 1
        return self._highest_label

    def transpile(self, tree):
        token = ''
        try:
            token = str(tree.data)
        except:
            token = str(tree)

        if token == "start" or token == "block":
            bytecode = []
            for i in tree.children:
                bytecode += self.transpile(i)
            return bytecode

        elif token == "var_dec":
            bytecode = []
            if str(tree.children[0].data) == 'iden':
                bytecode = ['puv', str(tree.children[0].children[0]), 'set']
            else:
                bytecode = ['puv', str(tree.children[0].children[0].children[0]),
                            'puv', str(tree.children[0].children[1].children[0]),
                            'puidx']

            return self.transpile(tree.children[1]) + bytecode

        elif token == "lit":
            val = str(tree.children[0])
            if val[0] == '"' and val[-1] == '"':
                val = val[1:-1]
            elif val.isnumeric():
                val = [float(val)]

            return ['puv', val]

        elif token in self.INFIX:
            return self.transpile(tree.children[0]) + self.transpile(tree.children[1]) + [token]

        elif token in self.PREFIX:
            return self.transpile(tree.children[0]) + [token]

        elif token in self.SELFFIX:
            bytecode = []
            if str(tree.children[0].data) == 'iden':
                bytecode = ['puv', str(tree.children[0].children[0]), 'set']
            else:
                bytecode = ['puv', str(tree.children[0].children[0].children[0]),
                            'puv', str(tree.children[0].children[1].children[0]),
                            'puidx']

            return self.transpile(tree.children[0]) + \
                   self.transpile(tree.children[1]) + \
                   [token[4:-1]] + \
                   bytecode

        elif token == 'inc':
            bytecode = []
            if str(tree.children[0].data) == 'iden':
                bytecode = ['puv', str(tree.children[0].children[0]), 'set']
            else:
                bytecode = ['puv', str(tree.children[0].children[0].children[0]),
                            'puv', str(tree.children[0].children[1].children[0]),
                            'puidx']

            return self.transpile(tree.children[0]) + \
                   self.transpile(tree.children[0]) + \
                   ['puv', [1], 'add'] + \
                   bytecode

        elif token == 'dec':
            bytecode = []
            if str(tree.children[0].data) == 'iden':
                bytecode = [str(tree.children[0].children[0]), 'set']
            else:
                bytecode = ['puv', str(tree.children[0].children[0].children[0]),
                            'puv', str(tree.children[0].children[1].children[0]),
                            'puidx']

            return self.transpile(tree.children[0]) + \
                   self.transpile(tree.children[0]) + \
                   ['puv', [1], 'sub'] + \
                   bytecode

        elif token == "iden":
            return ['puv', str(tree.children[0]), 'get']

        elif token == "lst_index":
            var = str(tree.children[0].children[0].children[0])
            idx = str(tree.children[0].children[1].children[0])

            return ['puv', var,
                    'puv', idx,
                    'poidx']

        elif token == "if":
            label = self._get_label()

            bytecode = self.transpile(tree.children[0]) + \
                       ['if', label] + \
                       self.transpile(tree.children[1]) + \
                       ['lbl', label]

            if len(tree.children) == 3:
                bytecode += self.transpile(tree.children[2])

            return bytecode

        elif token == "while":
            start = self._get_label()
            done = self._get_label()

            return ['lbl', start] + \
                   self.transpile(tree.children[0]) + \
                   ['if', done] + \
                   self.transpile(tree.children[1]) + \
                   ['lbl', done]

        elif token == "for":
            start = self._get_label()
            done = self._get_label()

            return self.transpile(tree.children[0]) + \
                   ['lbl', start] + \
                   self.transpile(tree.children[1]) + \
                   ['if', done] + \
                   self.transpile(tree.children[3]) + \
                   self.transpile(tree.children[2]) + \
                   ['goto', start] + \
                   ['lbl', done]

        elif token == "list":
            bytecode = []

            for i in tree.children:
                bytecode += self.transpile(i) + ['append']

            return bytecode

        elif token == "fun_dec":
            skip = self._get_label()
            iden = str(tree.children[0].children[0])
            bytecode = self.transpile(tree.children[-1])
            args = []

            for i in tree.children[-2:0:-1]:
                args += ['puv', str(i.children[0]), 'set']

            return ['goto', skip] + \
                   ['lbl', iden] + \
                   args + \
                   bytecode + \
                   ['poa'] + \
                   ['lbl', skip]

        elif token == "fun_call":
            iden = str(tree.children[0].children[0])
            args = []
            for i in tree.children[1:]:
                args += self.transpile(i)
            return args + ['pua', iden]

        raise NotImplementedError
