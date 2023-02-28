class Token:

    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __str__(self):
        return str(self.recognized_string) + '\tfamily:\"' + str(self.family) + '\",  line: ' + str(self.line_number)

#token = Token(")", "groupSymbol", 11)
#print(str(token))