from token import Token

class Lex:
    def __init__(self, file_name, file_pointer = None, current_line = 1):
        self.file_name = file_name
        self.file_pointer = open(file_name, "r")
        self.current_line = current_line

    #destructor
    def __del__(self):
        self.file_pointer.close()

    # def error(self, description):
    #     print("Error: ", description, "at line", self.current_line)
    #     exit()

    def next_token(self):
        buffer = ""
        state = "start"
        family = None
        
        while family == None and state != "error":
            input = self.file_pointer.read(1)

            if input == '\n':
                self.current_line += 1
            #alphanumeric
            elif (state == "start" or state == "dig") and input.isdigit():
                buffer += input
                state = "dig"
            elif state == "dig" and input.isalpha():
                state == "error"
            elif state == "dig" and not input.isdigit():
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                if abs(int(buffer)) > 4294967295:
                    state == "error"
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
                    state == "error"
                family = "identifierOrKeyword"
            #symbols
            elif state == "start" and input in ['{', '}', '(', ')', '[', ']']:
                buffer += input
                family = "groupSymbol"
            elif state == "start" and input in [',', ';', '.', ':']:
                buffer += input
                family = "delimeter"
            elif state == "start" and input == '#':
                buffer += input
                state = "inSharp"
            elif state == "inSharp" and input in ['{', '}']:
                buffer += input
                family = "groupSymbol"
            #comments
            elif state == "inSharp" and input == '$':
                state = "rem"
            elif state == "rem" and input == '':
                state = "error"
            elif state == "rem" and input == '#':
                state == "outSharp"
            elif state == "rem":
                continue
            elif state == "outSharp" and input == '$':
                state = "start"    
            #operators
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
            elif state == "start" and input == '<':
                buffer += input
                state = "smaller"
            elif state == "smaller" and input in ['>', '=']:
                buffer += input
                family = "relOperator"
            elif state == "smaller" and input not in ['>', '=']:
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                family = "relOperator"
            elif state == "start" and input == '>':
                buffer += input
                state = "larger"
            elif state == "larger" and input == '=':
                buffer += input
                family = "relOperator"
            elif state == "larger" and input != '=':
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                family = "relOperator"
            elif input.isspace():
                continue
            else:
                print("Error: unknown character ", input, " at line ", self.current_line, " state is ", state)
                exit()

        return Token(buffer, family, self.current_line)

lex = Lex("test.cpy")
token = lex.next_token()

while token != None:
    print(token)
    token = lex.next_token()

del lex