from token import Token

class Lex:
    def __init__(self, current_line, file_name, token):
        self.current_line = current_line
        self.file_name = file_name
        self.token = token

    #destructor
    #def __del__():

    #def error():

    def next_token():
        buffer = ""
        state = "start"
        family = None
        
        while family == None and state != "error":
            input = file_name.read(1)

            if input == '\n':
                current_line += 1
            elif input.isspace():
                #do nothing         
            #alphanumeric
            elif (state == "start" or state == "dig") and input.isdigit():
                buffer += input
                state = "dig"
            elif state == "dig" and not input.isdigit():
                unget()
                family = "number"
            elif state == "start" and input.isalpha():
                buffer += input
                state = "idk"
            elif state == "idk" and (input.isalpha() or input.isdigit()):
                buffer += input
                state = "idk"
            elif state == "idk" and not (input.isalpha() or input.isdigit()):
                unget()
                family = "identifierOrKeyword"
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
                unget()
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
                unget()
                family = "relOperator"
            elif state == "start" and input == '>':
                buffer += input
                state = "larger"
            elif state == "larger" and input == '=':
                buffer += input
                family = "relOperator"
            elif state == "larger" and input != '=':
                unget()
                family = "relOperator"
            #symbols
            elif state == "start" and input in ['{', '}', '(', ')', '[', ']']:
                buffer += input
                family = "groupSymbol"
            elif state == "start" and input in [',', ';', '.']:
                buffer += input
                family = "delimeter"
            #comments
            elif state == "start" and input == '#':
                state = "inSharp"
            elif state == "inSharp" and input == '$':
                state = "rem"
            elif state == "rem" and input == '#':
                state == "outSharp"
            elif state == "outSharp" and input == '$':
                state = "start"    

        return Token(buffer, family, current_line)
            
    def unget():
        file_name.seek(file_name.tell() - 1)

#lex = Lex(1, "lol.cpy", token)
#print(lex)
