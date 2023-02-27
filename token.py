class Token:

    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __str__():
        return  str(self.family) + ', ' + str(self.line_number) + ', ' + str(self.recognized_string)