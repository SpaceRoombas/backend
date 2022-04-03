class LangException(Exception):
    def __init__(self, line, text):
        self.value = f"error on line {line}: {text}"

    def __str__(self):
        return(repr(self.value))