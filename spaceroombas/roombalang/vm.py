import copy

from .exceptions import LangException

MAX_INSTRUCTIONS_PER_TICK = 100


class Stack:
    def __init__(self, parent=None, addr=None):
        self._parent = parent
        if parent is None:
            self._vars = {"true": [True], "false": [False], "pi": [3.14159265359], "north": [0], "east": [1],
                          "south": [2], "west": [3]}
        else:
            self._vars = {}
        self.addr = addr

    def setVar(self, iden, val):
        exists = self.hasVar(iden)
        if exists:
            self._changeVar(iden, val)
        else:
            self._makeVar(iden, val)

    def _changeVar(self, iden, val):
        if iden in self._vars.keys():
            self._vars[iden] = val
        else:
            self._parent._changeVar(iden, val)

    def _makeVar(self, iden, val):
        self._vars[iden] = val

    def getVar(self, iden):
        if iden in self._vars.keys():
            return copy.deepcopy(self._vars)[iden]
        elif self._parent is not None:
            return self._parent.getVar(iden)
        else:
            return None

    def hasVar(self, iden):
        if iden in self._vars.keys():
            return True
        elif self._parent is not None:
            return self._parent.hasVar(iden)
        else:
            return False

    def pushFrame(self, addr):
        return Stack(parent=self, addr=addr)

    def popFrame(self):
        return self.addr, self._parent


class VM:
    def __init__(self, external_fns):
        self.external_fns = external_fns
        self.call_stack = Stack()
        self.var_stack = []
        self.pointer = 0
        self.labels = {}

    # runs until an external fn is hit and then breaks returning the position of the pointer
    def tick(self, bytecode):

        executed = 0

        # set up labels
        for idx, i in enumerate(bytecode):
            if i == 'lbl':
                self.labels[bytecode[idx + 1]] = idx + 2

        # run bytecode
        while self.pointer != -1:

            executed += 1

            try:
                i = bytecode[self.pointer]

                if i == "goto":
                    self.pointer = self.labels[bytecode[self.pointer + 1]]

                elif i == "add":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] += a[0]

                    self.pointer += 1

                elif i == "sub":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] -= a[0]

                    self.pointer += 1

                elif i == "mul":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] *= a[0]

                    self.pointer += 1

                elif i == "div":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] /= a[0]

                    self.pointer += 1

                elif i == "exp":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] **= a[0]

                    self.pointer += 1

                elif i == "and":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] &= a[0]

                    self.pointer += 1

                elif i == "or":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] |= a[0]

                    self.pointer += 1

                elif i == "xor":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] ^= a

                    self.pointer += 1

                elif i == "rem":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] %= a

                    self.pointer += 1

                elif i == "idiv":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] //= a[0]

                    self.pointer += 1

                elif i == "neg":
                    self.var_stack[-1][0] = -self.var_stack[-1][0]

                    self.pointer += 1

                elif i == "eq":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] = self.var_stack[-1][0] == a[0]

                    self.pointer += 1

                elif i == "lt":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] = self.var_stack[-1][0] < a[0]

                    self.pointer += 1

                elif i == "mt":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] = self.var_stack[-1][0] > a[0]

                    self.pointer += 1

                elif i == "leq":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] = self.var_stack[-1][0] <= a[0]

                    self.pointer += 1

                elif i == "meq":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] = self.var_stack[-1][0] >= a[0]

                    self.pointer += 1

                elif i == "neq":
                    a = self.var_stack.pop()
                    self.var_stack[-1][0] = self.var_stack[-1][0] != a[0]

                    self.pointer += 1

                elif i == "pua":
                    label = bytecode[self.pointer + 1]
                    try:
                        new_ptr = self.labels[label]
                        self.call_stack = self.call_stack.pushFrame(self.pointer + 1)
                        self.pointer = new_ptr
                    except:
                        fn = self.external_fns[label]
                        args = []
                        for i in range(0, fn[1]):
                            args.append(self.var_stack.pop())
                        res = fn[0](args)
                        if res is not None:
                            self.var_stack.append([res])

                        self.pointer += 1
                        break

                elif i == "poa":
                    self.pointer, self.call_stack = self.call_stack.popFrame()

                elif i == "if":
                    a = self.var_stack.pop()[0]
                    if not a:
                        self.pointer = self.labels[bytecode[self.pointer + 1]]
                    else:
                        self.pointer += 1

                elif i == "get":
                    iden = self.var_stack.pop()
                    self.var_stack.append(self.call_stack.getVar(iden))

                    self.pointer += 1

                elif i == "set":
                    iden = self.var_stack.pop()
                    val = self.var_stack.pop()

                    self.call_stack.setVar(iden, val)

                    self.pointer += 1

                elif i == "app":
                    var = self.var_stack.pop()
                    val = self.var_stack.pop()
                    new_val = []

                    if len(val) == 1:
                        new_val = self.call_stack.getVar(var) + val
                    else:
                        self.call_stack.getVar(var).append(val)

                    self.call_stack.setVar(var, new_val)

                    self.pointer += 1

                elif i == "aps":
                    val = self.var_stack.pop()

                    if len(val) == 1:
                        self.var_stack[-1] += val
                    else:
                        self.var_stack[-1].append(val)

                    self.pointer += 1

                elif i == "puv":
                    self.var_stack.append(copy.deepcopy(bytecode)[self.pointer + 1])

                    self.pointer += 1

                elif i == "pov":
                    self.var_stack.pop()

                    self.pointer += 1

                elif i == "poidx":
                    index = self.var_stack.pop()
                    var = self.var_stack.pop()
                    self.var_stack.append(self.call_stack.getVar(var)[index])

                    self.pointer += 1

                elif i == "puidx":
                    index = self.var_stack.pop()
                    var = self.var_stack.pop()
                    new_val = self.var_stack.pop()
                    oldval = self.call_stack.getVar(var)
                    oldval[idx] = new_val
                    self.call_stack.setVar(var, oldval)

                    self.pointer += 1

                else:
                    self.pointer += 1

                if self.pointer >= len(bytecode):
                    self.pointer = -1
                    break

                if executed >= MAX_INSTRUCTIONS_PER_TICK:
                    break

            except Exception:
                print(f"vm crash at ins: {self.pointer}\n {bytecode[self.pointer]}")
                print(bytecode)

                raise LangException(-1, "Vm Error!")

        return self.pointer
