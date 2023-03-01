from token import Token

class Lex:
    def __init__(self, current_line, file_name, token):
        self.current_line = current_line
        self.file_name = file_name
        self.token = token

    #destructor
    #def __del__():

    #def error():

    def next_token(self):
        buffer = ""
        state = "start"
        family = None
        
        while family == None and state != "error":
            input = self.file_name.read(1)

            if input == '\n':
                self.current_line += 1
            elif input.isspace():
                continue
            #alphanumeric
            elif (state == "start" or state == "dig") and input.isdigit():
                buffer += input
                state = "dig"
            elif state == "dig" and input.isalpha():
                state == "error"
            elif state == "dig" and not input.isdigit():
                self.file_name.seek(self.file_name.tell() - 1)
                if abs(int(input)) > 4294967295:
                    state == "error"
                family = "number"
            elif state == "start" and input.isalpha():
                buffer += input
                state = "idk"
            elif state == "idk" and (input.isalpha() or input.isdigit() or input == '_'):
                buffer += input
                state = "idk"
            elif state == "idk" and not (input.isalpha() or input.isdigit()):
                self.file_name.seek(self.file_name.tell() - 1)
                if len(buffer) > 30:
                    state == "error"
                family = "identifierOrKeyword"
            #symbols
            elif state == "start" and input in ['{', '}', '(', ')', '[', ']']:
                buffer += input
                family = "groupSymbol"
            elif state == "start" and input in [',', ';', '.']:
                buffer += input
                family = "delimeter"
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
                self.file_name.seek(self.file_name.tell() - 1)
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
                self.file_name.seek(self.file_name.tell() - 1)
                family = "relOperator"
            elif state == "start" and input == '>':
                buffer += input
                state = "larger"
            elif state == "larger" and input == '=':
                buffer += input
                family = "relOperator"
            elif state == "larger" and input != '=':
                self.file_name.seek(self.file_name.tell() - 1)
                family = "relOperator"
            #comments
            elif state == "start" and input == '#':
                state = "inSharp"
            elif state == "inSharp" and input == '$':
                state = "rem"
            elif state == "rem" and input == '':
                state = "error"
            elif state == "rem" and input == '#':
                state == "outSharp"
            elif state == "outSharp" and input == '$':
                state = "start"    
            else:
                state = "error" 

        return Token(buffer, family, self.current_line)

f = open("factorial.cpy", "r")

l = Lex(0, f, None)

print(l.next_token())

f.close()
