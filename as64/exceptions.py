class AS64Exception(Exception):
    def __init__(self):
        self.code = '-1'
        self.message = "Unkown Error."