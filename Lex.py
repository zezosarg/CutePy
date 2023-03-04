from Token import Token

class Lex:
    def __init__(self, file_name, file_pointer = None, current_line = 1):
        self.file_name = file_name
        self.file_pointer = open(file_name, "r")
        self.current_line = current_line

    #destructor
    def __del__(self):
        self.file_pointer.close()

    def error(self, description = "no description"):
        print("Error: ", description, " at line ", self.current_line)
        exit()

    def next_token(self):
        buffer = ""
        state = "start"
        family = None
        
        while family == None:
            input = self.file_pointer.read(1)

            if input == '\n':
                self.current_line += 1

            elif (state == "start" or state == "dig") and input.isdigit():
                buffer += input
                state = "dig"
            elif state == "dig" and input.isalpha():
                self.error("found a letter attached to a number")
            elif state == "dig" and not input.isdigit():
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                if abs(int(buffer)) > 4294967295:
                    self.error("number exceeded limit")
                family = "number"

            elif state == "start" and input.isalpha():
                buffer += input
                state = "idk"
            elif state == "idk" and (input.isalpha() or input.isdigit() or input == '_'):
                buffer += input
                state = "idk"
            elif state == "idk" and not (input.isalpha() or input.isdigit()):
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                if len(buffer) > 30:
                    self.error("identifier or keyword exceeded limit")
                family = "identifierOrKeyword"

            elif state == "start" and input in ['{', '}', '(', ')', '[', ']', '"']:
                buffer += input
                family = "groupSymbol"

            elif state == "start" and input in [',', ';', '.', ':']:
                buffer += input
                family = "delimeter"

            elif state == "start" and input == '#':
                buffer += input
                state = "sharp"
            elif state == "sharp" and input not in ['$', '{', '}']:
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                family = "delimiter"
            elif state == "sharp" and input in ['{', '}']:
                buffer += input
                family = "groupSymbol"
            elif state == "sharp" and input == '$':
                buffer = ""
                state = "rem"
            elif state == "rem" and input == '':
                self.error("comments never closed")
            elif state == "rem" and input == '#':
                state = "endComment"
            elif state == "rem":
                continue
            elif state == "endComment" and input == '$':
                state = "start"

            elif state == "start" and input in ['+', '-']:
                buffer += input
                family = "addOperator"

            elif state == "start" and input == '*':
                buffer += input
                family = "mulOperator"

            elif state == "start" and input == '/':
                buffer += input
                state = "div"
            elif state == "div" and input == '/':
                buffer += input
                family = "mulOperator"

            elif state == "start" and input == '=':
                buffer += input
                state = "equal"
            elif state == "equal" and input != '=':
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                family = "assignment"
            elif state == "equal" and input == '=':
                buffer += input
                family = "relOperator"

            elif state == "start" and input == '!':
                buffer += input
                state = "mark"
            elif state == "mark" and input == '=':
                buffer += input
                family = "relOperator"
            elif state == "mark" and input != '=':
                self.error("character ! must be followed by =")
            
            elif state == "start" and input in ['<', '>']:
                buffer += input
                state = "rel"
            elif state == "rel" and input == '=':
                buffer += input
                family = "relOperator"
            elif state == "rel" and input != '=':
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                family = "relOperator"

            elif state == "start" and input == '_':
                buffer += input
                state = "underscore"
            elif state == "underscore" and input == '_':
                buffer += input
                family = "doubleUnderscore"
            elif state == "underscore" and input != '_':
                self.error("underscores must come in attached pairs")
            
            elif state == "start" and input.isspace():
                continue

            elif state == "start" and input == "":
                family = "EOF"
                self.error("end of file")

            else:
                self.error("potentially unknown character " + input)

        return Token(buffer, family, self.current_line)

lex = Lex("factorial.cpy")
token = lex.next_token()

while token.family != "error":
    print(token)
    token = lex.next_token()

del lex