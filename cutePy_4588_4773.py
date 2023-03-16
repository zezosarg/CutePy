# Argyrios Zezos, 4588, cse84588
# Fotios Pappas, 4773, cse94773

import re   # regular expressions
import sys  # for command line arguments

class Token:

    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __str__(self):
        return str(self.recognized_string) + '\tfamily:\"' + str(self.family) + '\",\tline: ' + str(self.line_number)

class Lex:
    def __init__(self, file_name, file_pointer = None, current_line = 1):
        self.file_name = file_name
        self.file_pointer = open(file_name, "r")
        self.current_line = current_line

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
            head = self.file_pointer.read(1)

            if head == '\n':
                self.current_line += 1

            elif state == "start" and head.isdigit():
                buffer += head
                state = "dig"
            elif state == "dig" and head.isdigit():
                buffer += head
                state = "dig"
            elif state == "dig" and head.isalpha():
                self.error("found a letter attached to a number")
            elif state == "dig" and not head.isdigit():
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                if abs(int(buffer)) > 4294967295:
                    self.error("number exceeded limit")
                family = "number"

            elif state == "start" and (head.isalpha() or head == '_'):
                buffer += head
                state = "idk"
            elif state == "idk" and (head.isalpha() or head.isdigit() or head == '_'):
                buffer += head
                state = "idk"
            elif state == "idk" and not (head.isalpha() or head.isdigit()):
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                if len(buffer) > 30:
                    self.error("identifier or keyword exceeded limit")
                keywords = ["not", "and", "or", "if", "else", "while", "return", "print", "def", "int", "input", "declare"]
                if buffer in keywords:
                    family = "keyword"
                else:
                    family = "identifier"  

            elif state == "start" and head in ['{', '}', '(', ')', '[', ']', '"']:
                buffer += head
                family = "groupSymbol"

            elif state == "start" and head in [',', ';', '.', ':']:
                buffer += head
                family = "delimeter"

            elif state == "start" and head == '#':
                buffer += head
                state = "sharp"
            elif state == "sharp" and head not in ['$', '{', '}']:
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                family = "delimiter"
            elif state == "sharp" and head in ['{', '}']:
                buffer += head
                family = "groupSymbol"
            elif state == "sharp" and head == '$':
                buffer = ""
                state = "rem"
            elif state == "rem" and head == '':
                self.error("comments never closed")
            elif state == "rem" and head == '#':
                state = "endComment"
            elif state == "rem":
                continue
            elif state == "endComment" and head == '$':
                state = "start"

            elif state == "start" and head in ['+', '-']:
                buffer += head
                family = "addOperator"

            elif state == "start" and head == '*':
                buffer += head
                family = "mulOperator"

            elif state == "start" and head == '/':
                buffer += head
                state = "div"
            elif state == "div" and head == '/':
                buffer += head
                family = "mulOperator"

            elif state == "start" and head == '=':
                buffer += head
                state = "equal"
            elif state == "equal" and head != '=':
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                family = "assignment"
            elif state == "equal" and head == '=':
                buffer += head
                family = "relOperator"

            elif state == "start" and head == '!':
                buffer += head
                state = "mark"
            elif state == "mark" and head == '=':
                buffer += head
                family = "relOperator"
            elif state == "mark" and head != '=':
                self.error("character ! must be followed by =")
            
            elif state == "start" and head in ['<', '>']:
                buffer += head
                state = "rel"
            elif state == "rel" and head == '=':
                buffer += head
                family = "relOperator"
            elif state == "rel" and head != '=':
                self.file_pointer.seek(self.file_pointer.tell() - 1)
                family = "relOperator"

            elif state == "start" and head.isspace():
                continue

            elif state == "start" and head == "":
                family = "eof"

            else:
                self.error("potentially unknown character " + head)

        return Token(buffer, family, self.current_line)

class Parser:
    def __init__(self, file_name):
        self.lexical_analyser = Lex(file_name)

    def syntax_analyzer(self):
        global token
        token = self.get_token()
        self.start_rule()
        print('compilation successfully completed')

    def get_token(self):
        next_token = self.lexical_analyser.next_token()
        print("token:", next_token)
        return next_token

    def error(self, description = "no description"):
        print("Error:", description, " at line:", token.line_number, " token.recognized_string:", token.recognized_string)
        exit()

    def start_rule(self):
        self.def_main_part()
        self.call_main_part()

    def def_main_part(self):
        global token
        self.def_main_function()
        while token.recognized_string == "def":
            self.def_main_function()

    def def_main_function(self):
        global token
        if token.recognized_string == "def":
            token = self.get_token()
            if token.family == "identifier" and re.search("^main_[a-zA-Z0-9]+", token.recognized_string): # Starts with "main_" and has at least one letter or digit after
                token = self.get_token()
                if token.recognized_string == "(":
                    token = self.get_token()
                    if token.recognized_string == ")":
                        token = self.get_token()
                        if token.recognized_string == ":":
                            token = self.get_token()
                            if token.recognized_string == "#{":
                                token = self.get_token()
                                self.declarations()
                                while token.recognized_string == "def":
                                    token = self.get_token()
                                    self.def_function()
                                self.statements()
                                if token.recognized_string == "#}":
                                    token = self.get_token()
                                else:
                                    self.error("Expected '#}' in def_main_function")
                            else:
                                self.error("Expected '#{' in def_main_function")
                        else:
                            self.error("Expected ':' in def_main_function")
                    else:
                        self.error("Expected ')' in def_main_function")
                else:
                    self.error("Expected '(' in def_main_function")
            else:
                self.error("Expected identifier that starts with 'main_' in def_main_function")
        else:
            self.error("Expected keyword 'def' in def_main_function")

    def def_function(self):
        global token
        if token.family == "identifier" and re.search("^(?!main_)", token.recognized_string): # Does not start with "main_"
            token = self.get_token()
            if token.recognized_string == "(":
                token = self.get_token()
                self.id_list()
                if token.recognized_string == ")":
                    token = self.get_token()
                    if token.recognized_string == ":":
                        token = self.get_token()
                        if token.recognized_string == "#{":
                            token = self.get_token()
                            self.declarations()
                            while token.recognized_string == "def":
                                token = self.get_token()
                                self.def_function()
                            self.statements()
                            if token.recognized_string == "#}":
                                token = self.get_token()
                            else:
                                self.error("Expected '#}' in def_function")
                        else:
                            self.error("Expected '#{' in def_function")
                    else:
                        self.error("Expected ':' in def_function")
                else:
                    self.error("Expected ')' in def_function")
            else:
                self.error("Expected '(' in def_function")
        else:
            self.error("Expected identifier in def_function")

    def declarations(self):
        global token
        while token.recognized_string == "#":
            token = self.get_token()
            self.declaration_line()
            
    def declaration_line(self):
        global token
        if token.recognized_string == "declare":
            token = self.get_token()
            self.id_list()
        else:
            self.error("Expected 'declare' keyword after '#' in declaration_line")

    def statement(self):
        if token.recognized_string == "if" or token.recognized_string == "while":
            self.structured_statement()
        else:
            self.simple_statement()

    def statements(self):
        self.statement()
        while token.recognized_string in ["if", "while", "identifier", "print", "return"] or token.family == "identifier":
            self.statement()

    def simple_statement(self):
        if token.recognized_string == "print":
            self.print_stat()
        elif token.recognized_string == "return":
            self.return_stat()
        elif token.family == "identifier":
            self.assignment_stat()
        else:
            self.error("Expected 'print', 'return' or identifier in simple_statement")

    def structured_statement(self):
        if token.recognized_string == "if":
            self.if_stat()
        elif token.recognized_string == "while":
            self.while_stat()
        else:
            self.error("Expected 'if' or 'while' in structured_statement")

    def assignment_stat(self):
        global token
        token = self.get_token()
        if token.recognized_string == "=":
            token = self.get_token()
            if token.recognized_string == "int":
                token = self.get_token()
                if token.recognized_string == "(":
                    token = self.get_token()
                    if token.recognized_string == "input":
                        token = self.get_token()
                        if token.recognized_string == "(":
                            token = self.get_token()
                            if token.recognized_string == ")":
                                token = self.get_token()
                                if token.recognized_string == ")":
                                    token = self.get_token()
                                    if token.recognized_string == ";":
                                        token = self.get_token()
                                    else:
                                        self.error("Expected ';' in assignment_stat")
                                else:
                                    self.error("Expected ')' in assignment_stat")
                            else:
                                self.error("Expected ')' in assignment_stat")
                        else:
                            self.error("Expected '(' in assignment_stat")
                    else:
                        self.error("Expected 'input' in assignment_stat")
                else:
                    self.error("Expected '(' in assignment_stat")
            else:
                self.expression()
                if token.recognized_string == ";":
                    token = self.get_token()
                else:
                    self.error("Expected ';' in assignment_stat")
        else:
            self.error("Expected '=' in assignment_stat")

    def print_stat(self):
        global token
        token = self.get_token()
        if token.recognized_string == "(":
            token = self.get_token()
            self.expression()
            if token.recognized_string == ")":
                token = self.get_token()
                if token.recognized_string == ";":
                    token = self.get_token()
                else:
                    self.error("Expected ';' in print_stat")
            else:
                self.error("Expected ')' in print_stat")
        else:
            self.error("Expected '(' in print_stat")

    def return_stat(self):
        global token
        token = self.get_token()
        if token.recognized_string == "(":
            token = self.get_token()
            self.expression()
            if token.recognized_string == ")":
                token = self.get_token()
                if token.recognized_string == ";":
                    token = self.get_token()
                else:
                    self.error("Expected ';' in return_stat")
            else:
                self.error("Expected ')' in return_stat")
        else:
            self.error("Expected '(' in return_stat")

    def if_stat(self):
        global token
        token = self.get_token()
        if token.recognized_string == "(":
            token = self.get_token()
            self.condition()
            if token.recognized_string == ")":
                token = self.get_token()
                if token.recognized_string == ":":
                    token = self.get_token()
                    if token.recognized_string == "#{":
                        token = self.get_token()
                        self.statements()
                        if token.recognized_string == "#}":
                            token = self.get_token()
                        else:
                            self.error("Expected '#}' in if_stat")
                    else:
                        self.statement()
                    if token.recognized_string == "else":
                        token = self.get_token()
                        if token.recognized_string == ":":
                            token = self.get_token()
                            if token.recognized_string == "#{":
                                token = self.get_token()
                                self.statements()
                                if token.recognized_string == "#}":
                                    token = self.get_token()
                                else:
                                    self.error("Expected '#}' in if_stat")
                            else:
                                self.statement()
                else:
                    self.error("Expected ':' in if_stat")
            else:
                self.error("Expected ')' in if_stat")
        else:
            self.error("Expected '(' in if_stat")

    def while_stat(self):
        global token
        token = self.get_token()
        if token.recognized_string == "(":
            token = self.get_token()
            self.condition()
            if token.recognized_string == ")":
                token = self.get_token()
                if token.recognized_string == ":":
                    token = self.get_token()
                    if token.recognized_string == "#{":
                        token = self.get_token()
                        self.statements()
                        if token.recognized_string == "#}":
                            token = self.get_token()
                        else:
                            self.error("Expected '#}' in while_stat")
                    else:
                        self.statement()
                else:
                    self.error("Expected ':' in while_stat")
            else:
                self.error("Expected ')' in while_stat")
        else:
            self.error("Expected '(' in while_stat")

    def id_list(self):
        global token
        if token.family == "identifier":
            token = self.get_token()
            while token.recognized_string == ",":
                token = self.get_token()
                if token.family == "identifier":
                    token = self.get_token()
                else:
                    self.error("Expected an identifier in id_list")

    def expression(self):
        global token
        self.optional_sign()
        self.term()
        while token.recognized_string == "+" or token.recognized_string == "-":
            token = self.get_token()
            self.term()

    def term(self):
        global token
        self.factor()
        while token.recognized_string == "*" or token.recognized_string == "//":
            token = self.get_token()
            self.factor()

    def factor(self):
        global token
        if token.recognized_string.isnumeric():
            token = self.get_token()
        elif token.recognized_string == "(":
            token = self.get_token()
            self.expression()
            if token.recognized_string == ")":
                token = self.get_token()
            else:
                self.error("Expected ')' in factor")
        elif token.family == "identifier" and re.search("^(?!main_)", token.recognized_string):
            token = self.get_token()
            self.idtail()
        else:
            self.error("Expected integer or expression or non main identifier in factor")

    def idtail(self):
        global token
        if token.recognized_string == "(":
            token = self.get_token()
            self.actual_par_list()
            if token.recognized_string == ")":
                token = self.get_token()
            else:
                self.error("Expected ')' in idtail")

    def actual_par_list(self):
        global token
        self.expression()
        while token.recognized_string == ",":
            token = self.get_token()
            self.expression()

    def optional_sign(self):
        global token
        if token.recognized_string == "+" or token.recognized_string == "-":
            token = self.get_token()
        
    def condition(self):
        global token
        self.bool_term()
        while token.recognized_string == "or":
            token = self.get_token()
            self.bool_term()

    def bool_term(self):
        global token
        self.bool_factor()
        while token.recognized_string == "and":
            token = self.get_token()
            self.bool_factor()

    def bool_factor(self):
        global token
        if token.recognized_string == "not":
            token = self.get_token()
            if token.recognized_string == "[":
                token = self.get_token()
                self.condition()
                if token.recognized_string == "]":
                    token = self.get_token()
                else:
                    self.error("Expected ']' in bool_factor")
            else:
                self.error("Expected '[' in bool_factor")
        elif token.recognized_string == "[":
            token = self.get_token()
            self.condition()
            if token.recognized_string == "]":
                token = self.get_token()
            else:
                self.error("Expected ']' in bool_factor")
        else:
            self.expression()
            if token.recognized_string in ["==", "<", ">", ">=", "<=", "!="]:
                token = self.get_token()
            else:
                self.error("Expected relational operator in bool_factor")
            self.expression()

    def call_main_part(self):
        global token
        if token.recognized_string == "if":
            token = self.get_token()
            if token.recognized_string == "__name__":
                token = self.get_token()
                if token.recognized_string == "==":
                    token = self.get_token()
                    if token.recognized_string == '"':
                        token = self.get_token()
                        if token.recognized_string == "__main__":
                            token = self.get_token()
                            if token.recognized_string == '"':
                                token = self.get_token()
                                if token.recognized_string == ":":
                                    token = self.get_token()
                                    self.main_function_call()
                                    while token.family == "identifier":
                                        self.main_function_call()
                                else:
                                    self.error("Expected ':' in call_main_part")
                            else:
                                self.error("Expected quote in call_main_part")
                        else:
                            self.error("Expected '__main__' in call_main_part")
                    else:
                        self.error("Expected quote in call_main_part")
                else:
                    self.error("Expected '==' in call_main_part")
            else:
                self.error("Expected '__name__' in call_main_part")
        else:
            self.error("Expected 'if' in call_main_part")

    def main_function_call(self):
        global token
        if token.family == "identifier":
            token = self.get_token()
            if token.recognized_string == "(":
                token = self.get_token()
                if token.recognized_string == ")":
                    token = self.get_token()
                    if token.recognized_string == ";":
                        token = self.get_token()
                    else:
                        self.error("Expected ';' in main_function_call")
                else:
                    self.error("Expected ')' in main_function_call")
            else:
                self.error("Expected '(' in main_function_call") 
        else:
            self.error("Expected identifier in main_function_call")

parser = Parser(sys.argv[1])
parser.syntax_analyzer()
