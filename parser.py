from lex import Lex

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
            token = self.get_token()
            self.def_main_function()

    def def_main_function(self):
        global token
        if token.recognized_string == "def":
            token = self.get_token()
            if token.family == "identifierOrKeyword":
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
                self.error("Expected identifier in def_main_function")
        else:
            self.error("Expected keyword 'def' in def_main_function")

    def def_function(self):
        global token
        if token.family == "identifierOrKeyword":
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
        while token.recognized_string == "if" or token == "while" or token == "ID" or token == "print" or token == "return":
            self.statement()

    def simple_statement(self):
        if token.recognized_string == "print":
            self.print_stat()
        elif token.recognized_string == "return":
            self.return_stat()
        elif token.family == "identifierOrKeyword": #this string should be "identifier" but this family doesn't exit. maybe a disctinction between keywords and identifiers should be made.
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
        if token.family == "identifierOrKeyword":
            token = self.get_token()
            while token.recognized_string == ",":
                token = self.get_token()
                if token.family == "identifierOrKeyword":
                    token = self.get_token()
                else:
                    self.error("Expected an identifier in id_list")

    def expression(self):
        global token
        self.optional_sign()
        self.term()
        while token.recognized_string == "+" or token == "-":
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
        elif token.family == "identifierOrKeyword":
            token = self.get_token()
            self.idtail()
        else:
            self.error("Expected integer or expression or identifier in factor")

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
            if token.recognized_string == "==" or token.recognized_string == "<" or token.recognized_string == ">" or token.recognized_string == "!=" or token.recognized_string == "<=" or token.recognized_string == ">=":
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
                        if token.recognized_string == "__main__":
                            token == self.get_token()
                            if token.recognized_string == '"':
                                if token.recognized_string == ":":
                                    token = self.get_token()
                                    self.main_function_call()
                                    while token.family == "identifierOrKeyword":
                                        token = self.get_token()
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
        if token.family == "identifierOrKeyword":
            token == self.get_token()
            if token.recognized_string == "(":
                token = self.get_token()
                if token.recognized_string == ")":
                    token = self.get_token()
                    if token.recognized_string == ";":
                        token == self.get_token()
                    else:
                        self.error("Expected ';' in main_function_call")
                else:
                    self.error("Expected ')' in main_function_call")
            else:
                self.error("Expected '(' in main_function_call") 
        else:
            self.error("Expected identifier in main_function_call")
