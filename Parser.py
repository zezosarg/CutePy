from Lex import Lex

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

    def def_main_part(self):
        global token
        self.def_main_function()
        while token.recognized_string == "def":
            token = self.get_next_token()
            self.def_main_function()

    def start_rule():
        def_main_part()
        call_main_part()

    def def_main_function(self):
        if token.recognized_string == "def":
            if token.recognized_string == "ID":  # ID is a valid function name, maybe with regex
                token = self.get_next_token()
                if token.recognized_string == "(":
                    token = self.get_next_token()
                    if token.recognized_string == ")":
                        token = self.get_next_token()
                        if token.recognized_string == ":":
                            token = self.get_next_token()
                            if token.recognized_string == "#{":
                                token = self.get_next_token()
                                declarations()
                                while token.recognized_string == "def":
                                    def_function()
                                statements()
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
                self.error("")
        else:
            self.error("keyword'def' expected at start of program")


    def def_function(self):
        if token.recognized_string == "ID":
            token = self.get_next_token()
            if token.recognized_string == "(":
                token = self.get_next_token()
                id_list()
                if token.recognized_string == ")":
                    token = self.get_next_token()
                    if token.recognized_string == ":":
                        token = self.get_next_token()
                        if token.recognized_string == "#{":
                            token = self.get_next_token()
                            declarations()
                            while token.recognized_string == "def":
                                def_function()
                            statements()
                            if token.recognized_string == "#}":
                                token = self.get_next_token()
                            else:
                                self.error("Expected '#}'")

                        else:
                            self.error("Expected '#{'")
                    else:
                        self.error("Expected ':'")
                else:
                    self.error("Expected '('")


    def declarations():
        while token.recognized_string == "#declare":
            declaration_line()


    def declaration_line(self):
        token = self.get_next_token()
        id_list()


    def statement():
        if token.recognized_string == "if" or token == "while":
            structured_statement()
        else:
            simple_statement()


    def statements():
        statement()
        while token.recognized_string == "if" or token == "while" or token == "ID" or token == "print" or token == "return":
            statement()


    def simple_statement(self):
        if token.recognized_string == "ID":
            assignment_stat()
        elif token.recognized_string == "print":
            print_stat()
        elif token.recognized_string == "return":
            return_stat()
        else:
            self.error("Token doesn't exist")


    def structured_statement(self):
        if token.recognized_string == "if":
            if_stat()
        elif token.recognized_string == "while":
            while_stat()
        else:
            self.error("Token doesn't exist")


    def assignment_stat(self):  # Oi parentheseis paizoyn kapoio rolo sthn grammatiki?
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
                expression()
                if token.recognized_string == ";":
                    token = self.get_next_token()
                else:
                    self.error("Expected ';'")
        else:
            self.error("Expected '='")


    def print_stat(self):
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            expression()
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
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            expression()
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
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            condition()
            if token.recognized_string == ")":
                token = self.get_next_token()
                if token.recognized_string == ":":
                    token = self.get_next_token()
                    if token.recognized_string == "#{":
                        statements()
                        if token.recognized_string == "#}":
                            token = self.get_next_token()
                        else:
                            self.error("Expected '#}'")
                    else:
                        statement()
                    if token.recognized_string == "else":
                        token = self.get_next_token()
                        if token.recognized_string == ":":
                            token = self.get_next_token()
                            if token.recognized_string == "#{":
                                statements()
                                if token.recognized_string == "#}":
                                    token = self.get_next_token()
                                else:
                                    self.error("Expected '#}'")
                            else:
                                statement()
                else:
                    self.error("Expected ':'")
            else:
                self.error("Expected ')'")
        else:
            self.error("Expected '('")

    def while_stat(self):
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            condition()
            if token.recognized_string == ")":
                token = self.get_next_token()
                if token.recognized_string == ":":
                    token = self.get_next_token()
                    if token.recognized_string == "#{":
                        statements()
                        if token.recognized_string == "#}":
                            token = self.get_next_token()
                        else:
                            self.error("Expected '#}'")
                    else:
                        statement()
                else:
                    self.error("Expected ':'")
            else:
                self.error("Expected ')'")
        else:
            self.error("Expected '('")

    def id_list(self):
        if token.recognized_string == "ID":
            token = self.get_next_token()
            while token.recognized_string == ",":
                token = self.get_next_token()
                if token.recognized_string == "ID":
                    token = self.get_next_token()
                else:
                    self.error("Expected a parameter")

    def expression(self):
        optional_sign()
        term()
        while token.recognized_string == "+" or token == "-":
            token = self.get_next_token()
            term()

    def factor(self):
        if token.isnumeric():
            token = self.get_next_token()
        elif token.recognized_string == "(":
            token = self.get_next_token()
            expression()
            if token.recognized_string == ")":
                token = self.get_next_token()
            else:
                self.error("Expected ')'")
        elif token.recognized_string == "ID":
            token = self.get_next_token()
            idtail()
        else:
            self.error("Expected a factor") # better error?

    def term(self):
        factor()
        while token.recognized_string == "*" or token == "//":
            token = self.get_next_token()
            factor()


    def idtail(self):
        token = self.get_next_token()
        if token.recognized_string == "(":
            token = self.get_next_token()
            if token.recognized_string == ")":
                token = self.get_next_token()
            else:
                actual_par_list()
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
    
"""
"""