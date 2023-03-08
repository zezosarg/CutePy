from lex import Lex

class Parser:
    def __init__(self, fileInput):
        self.lexical_analyser = Lex(fileInput)

    def syntax_analyzer(self):
        global token
        token = self.get_next_token()
        self.start_rule()
        print('compilation successfully completed')

    def get_next_token(self):
        return self.lexical_analyser.next_token()

    def error(self, description = "no description"):
        print("Error: ", description, " at line ", token.current_line)
        exit()

    def start_rule(self):
        def_main_part()
        call_main_part()

    def def_main_part(self):
        global token
        self.def_main_function()
        while token.recognized_string == "def":
            token = self.get_next_token()
            self.def_main_function()

    def def_main_function(self):
        global token
        if token.recognized_string == "def":
            if token.family == "identifierOrKeyword":
                token = self.get_next_token()
                if token.recognized_string == "(":
                    token = self.get_next_token()
                    if token.recognized_string == ")":
                        token = self.get_next_token()
                        if token.recognized_string == ":":
                            token = self.get_next_token()
                            if token.recognized_string == "#{":
                                token = self.get_next_token()
                                self.declarations()
                                while token.recognized_string == "def":
                                    token = self.get_next_token()
                                    self.def_function()
                                self.statements()
                                if token.recognized_string == "#}":
                                    token = self.get_next_token()
                                else:
                                    self.error("Expected '#}'")
                            else:
                                self.error("Expected '#{'")
                        else:
                            self.error("Expected ':'")
                    else:
                        self.error("Expected ')'")
                else:
                    self.error("Expected '('")
            else:
                self.error("Expected identifier")
        else:
            self.error("Expected keyword 'def'")

    def def_function(self):
        global token
        if token.family == "identifierOrKeyword":
            token = self.get_next_token()
            if token.recognized_string == "(":
                token = self.get_next_token()
                self.id_list()
                if token.recognized_string == ")":
                    token = self.get_next_token()
                    if token.recognized_string == ":":
                        token = self.get_next_token()
                        if token.recognized_string == "#{":
                            token = self.get_next_token()
                            self.declarations()
                            while token.recognized_string == "def":
                                token = self.get_next_token()
                                self.def_function()
                            self.statements()
                            if token.recognized_string == "#}":
                                token = self.get_next_token()
                            else:
                                self.error("Expected '#}'")
                        else:
                            self.error("Expected '#{'")
                    else:
                        self.error("Expected ':'")
                else:
                    self.error("Expected ')'")
            else:
                self.error("Expected '('")
        else:
            self.error("Expected identifier")

    def declarations():
        global token
        while token.recognized_string == "#":
            token = self.get_next_token()
            self.declaration_line()
            
    def declaration_line(self):
        global token
        if token.recognized_string == "declare":
            token = self.get_next_token()
            self.id_list()
        else:
            self.error("Expected 'declare' keyword after '#'")

    def statement():
        if token.recognized_string == "if" or token.recognized_string == "while":
            self.structured_statement()
        else:
            self.simple_statement()

    def statements():
        statement()
        while token.recognized_string == "if" or token == "while" or token == "ID" or token == "print" or token == "return":
            statement()

    def simple_statement(self):
        if token.recognized_string == "print":
            self.print_stat()
        elif token.recognized_string == "return":
            self.return_stat()
        elif token.family == "identifierOrKeyword": #this string should be "identifier" but this family doesn't exit. maybe a disctinction between keywords and identifiers should be made.
            self.assignment_stat()
        else:
            self.error("Token doesn't exist")

    def structured_statement(self):
        if token.recognized_string == "if":
            self.if_stat()
        elif token.recognized_string == "while":
            self.while_stat()
        else:
            self.error("Token doesn't exist")

    def assignment_stat(self):
        global token
        token = self.get_next_token()
        if token.recognized_string == "=":
            token = self.get_next_token()
            if token.recognized_string == "int":
                token = self.get_next_token()
                if token.recognized_string == "(":
                    token = self.get_next_token()
                    if token.recognized_string == "input":
                        token = self.get_next_token()
                        if token.recognized_string == "(":
                            token = self.get_next_token()
                            if token.recognized_string == ")":
                                token = self.get_next_token()
                                if token.recognized_string == ")":
                                    token = self.get_next_token()
                                    if token.recognized_string == ";":
                                        token = self.get_next_token()
                                    else:
                                        self.error("Expected ';'")
                                else:
                                    self.error("Expected ')'")
                            else:
                                self.error("Expected ')'")
                        else:
                            self.error("Expected '('")
                    else:
                        self.error("Expected 'input'")
                else:
                    self.error("Expected '('")
            else:
                self.expression()
                if token.recognized_string == ";":
                    token = self.get_next_token()
                else:
                    self.error("Expected ';'")
        else:
            self.error("Expected '='")

    def print_stat(self):
        global token
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            self.expression()
            if token.recognized_string == ")":
                token = self.get_next_token()
                if token.recognized_string == ";":
                    token = self.get_next_token()
                else:
                    self.error("Expected ';'")
            else:
                self.error("Expected ')'")
        else:
            self.error("Expected '('")

    def return_stat(self):
        global token
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            self.expression()
            if token.recognized_string == ")":
                token = self.get_next_token()
                if token.recognized_string == ";":
                    token = self.get_next_token()
                else:
                    self.error("Expected ';'")
            else:
                self.error("Expected ')'")
        else:
            self.error("Expected '('")

    def if_stat(self):
        global token
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            self.condition()
            if token.recognized_string == ")":
                token = self.get_next_token()
                if token.recognized_string == ":":
                    token = self.get_next_token()
                    if token.recognized_string == "#{":
                        token = self.get_next_token()
                        self.statements()
                        if token.recognized_string == "#}":
                            token = self.get_next_token()
                        else:
                            self.error("Expected '#}'")
                    else:
                        self.statement()
                    if token.recognized_string == "else":
                        token = self.get_next_token()
                        if token.recognized_string == ":":
                            token = self.get_next_token()
                            if token.recognized_string == "#{":
                                token = self.get_next_token()
                                self.statements()
                                if token.recognized_string == "#}":
                                    token = self.get_next_token()
                                else:
                                    self.error("Expected '#}'")
                            else:
                                self.statement()
                else:
                    self.error("Expected ':'")
            else:
                self.error("Expected ')'")
        else:
            self.error("Expected '('")

    def while_stat(self):
        global token
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            self.condition()
            if token.recognized_string == ")":
                token = self.get_next_token()
                if token.recognized_string == ":":
                    token = self.get_next_token()
                    if token.recognized_string == "#{":
                        token = self.get_next_token()
                        self.statements()
                        if token.recognized_string == "#}":
                            token = self.get_next_token()
                        else:
                            self.error("Expected '#}'")
                    else:
                        self.statement()
                else:
                    self.error("Expected ':'")
            else:
                self.error("Expected ')'")
        else:
            self.error("Expected '('")

    def id_list(self):
        global token
        if token.family == "identifierOrKeyword":
            token = self.get_next_token()
            while token.recognized_string == ",":
                token = self.get_next_token()
                if token.family == "identifierOrKeyword":
                    token = self.get_next_token()
                else:
                    self.error("Expected an identifier")

    def expression(self):
        global token
        self.optional_sign()
        self.term()
        while token.recognized_string == "+" or token == "-":
            token = self.get_next_token()
            self.term()

    def term(self):
        self.factor()
        while token.recognized_string == "*" or token.recognized_string == "//":
            token = self.get_next_token()
            self.factor()

    def factor(self):
        global token
        if token.recognized_string.isnumeric():
            token = self.get_next_token()
        elif token.recognized_string == "(":
            token = self.get_next_token()
            self.expression()
            if token.recognized_string == ")":
                token = self.get_next_token()
            else:
                self.error("Expected ')'")
        elif token.family == "identifierOrKeyword":
            token = self.get_next_token()
            self.idtail()
        else:
            self.error("Expected integer or expression or identifier")

    def idtail(self):
        global token
        if token.recognized_string == "(":
            token = self.get_next_token()
            self.actual_par_list()
            if token.recognized_string == ")":
                    token = self.get_next_token()
                else:
                    self.error("Expected ')'")

    def actual_par_list(self):
        expression()
        while token.recognized_string == ",":
            token = self.get_next_token()
            expression()

    def optional_sign(self):
        if token.recognized_string == "+" or token.recognized_string == "-":
            token = self.get_next_token()
        
    def condition(self):
        bool_term()
        while token.recognized_string == "or":
            token = self.get_next_token()
            bool_term()

    def bool_term(self):
        bool_factor
        while token.recognized_string == "and":
            token = self.get_next_token()
            bool_factor()

    def bool_factor(self):
        if token.recognized_string == "not":
            token = self.get_next_token()
            if token.recognized_string == "[":
                token = self.get_next_token()
                condition()
                if token.recognized_string == "]":
                    token = self.get_next_token()
                else:
                    self.error("Expected ']'")
            else:
                self.error("Expected '['")
        elif token.recognized_string == "[":
            token = self.get_next_token()
            condition()
            if token.recognized_string == "]":
                token = self.get_next_token()
            else:
                self.error("Expected ']'")
        else:
            expression()
            if token.recognized_string == "==" or token.recognized_string == "<" or token.recognized_string == ">" or token.recognized_string == "!=" or token.recognized_string == "<=" or token.recognized_string == ">=":
                token = self.get_next_token()
            else:
                self.error("Expected relational operator")
            expression()

    def call_main_part(self):
        if token.recognized_string == "if":
            token = self.get_next_token()
            if token.recognized_string == "__name__":
                token = self.get_next_token()
                if token.recognized_string == "==":
                    token = self.get_next_token()
                    if token.recognized_string == "__main__":
                        token == self.get_next_token()
                        if token.recognized_string == ":":
                            token = self.get_next_token()
                            main_function_call()
                            while token.recognized_string == "ID":
                                main_function_call()
                        else:
                            self.error("Expected ':'") # better error?
                    else:
                        self.error("Expected '__main__'") # better error?
                else:
                    self.error("Expected '=='") # better error?
            else:
                self.error("Expected '__name__'") # better error?
        else:
            self.error("Expected 'if'") # better error?

    def main_function_call(self):
        if token.recognized_string == "ID":
            token == self.get_next_token()
            if token.recognized_string == "(":
                token = self.get_next_token()
                if token.recognized_string == ")":
                    token = self.get_next_token()
                    if token.recognized_string == ";":
                        token == self.get_next_token()
                    else:
                        self.error("Expected ';'")
                else:
                    self.error("Expected ')'")
            else:
                self.error("Expected '('") 
        else:
            self.error("Expected 'ID'")  # better error?      
