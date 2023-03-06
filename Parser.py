from Lex import Lex

class Parser:
    def __init__(self, lexical_analyser):
        self.lexical_analyser = lexical_analyser

    def syntax_analyzer():
        global token
        token = self.get_token()
        self.start_rule()
        print('compilation successfully completed')

    def get_token():
        return lexical_analyser.next_token()

    def error(self, description = "no description"):
        print("Error: ", description, " at line ", token.current_line)
        exit()

    def start_rule():
        def_main_part()
        call_main_part()

    def def_main_part():
        global token
        self.def_main_function()
        while (token.recognized_string == "def"):
            token = self.get_token()
            self.def_main_function()

    def def_main_function():
        if token.recognized_string == "def":
            if token == "ID":  # ID is a valid function name, maybe with regex
                token = get_token()
                if token == "(":
                    token = get_token()
                    if token == ")":
                        token = get_token()
                        if token == ":":
                            token = get_token()
                            if token == "#{":
                                token = get_token()
                                declarations()
                                while (token == "def"):
                                    def_function()
                                statements()
                                if token == "#}":
                                    token = get_token()
                                else:
                                    print("Expected '#}'")
                            else:
                                print("Expected '#{'")
                        else:
                            print("Expected ':'")
                    else:
                        print("Expected ')'")
                else:
                    print("Expected '('")
            else:
                self.error("")
        else:
            self.error("keyword'def' expected at start of program")

'''

    def def_function():
        if token == "ID"):
            token = get_token()
            if token == "("):
                token = get_token()
                id_list()
                if token == ")"):
                    token = get_token()
                    if token == ":"):
                        token = get_token()
                        if token == "#{"):
                            token = get_token()
                            declarations()
                            while (token == "def"):
                                def_function()
                            statements()
                            if token == "#}"):
                                token = get_token()
                            else:
                                print("Expected '#}'")

                        else:
                            print("Expected '#{'")
                    else:
                        print("Expected ':'")
                else:
                    print("Expected '('")


    def declarations():
        while (token == "#declare"):
            declaration_line()


    def declaration_line():
        token = get_token()
        id_list()


    def statement():
        if token == "if" or token == "while"):
            structured_statement()
        else:
            simple_statement()


    def statements():
        statement()
        while (token == "if" or token == "while"
            or token == "ID" or token == "print"
            or token == "return"):
            statement()


    def simple_statement():
        if token == "ID"):
            assignment_stat()
        elif token == "print"):
            print_stat()
        elif token == "return"):
            return_stat()
        else:
            print("Token doesn't exist")


    def structured_statement():
        if token == "if"):
            if_stat()
        elif token == "while"):
            while_stat()
        else:
            print("Token doesn't exist")


    def assignment_stat():  # Oi parentheseis paizoyn kapoio rolo sthn grammatiki?
        token = get_token()
        if token == "="):
            token = get_token()
            if token == "int"):
                token = get_token()
                if token == "("):
                    token = get_token()
                    if token == "input"):
                        token = get_token()
                        if token == "("):
                            token = get_token()
                            if token == ")"):
                                token = get_token()
                                if token == ")"):
                                    token = get_token()
                                    if token == ";"):
                                        token = get_token()
                                    else:
                                        print("Expected ';'")
                                else:
                                    print("Expected ')'")
                            else:
                                print("Expected ')'")
                        else:
                            print("Expected '('")
                    else:
                        print("Expected 'input'")
                else:
                    print("Expected '('")
            else:
                expression()
                if token == ";"):
                    token = get_token()
                else:
                    print("Expected ';'")
        else:
            print("Expected '='")


    def print_stat():
        token = get_token()
        if token == "("):
            token = get_token()
            expression()
            if token == ")"):
                token = get_token()
                if token == ";"):
                    token = get_token()
                else:
                    print("Expected ';'")
            else:
                print("Expected ')'")
        else:
            print("Expected '('")

    def return_stat():
        token = get_token()
        if token == "("):
            token = get_token()
            expression()
            if token == ")"):
                token = get_token()
                if token == ";"):
                    token = get_token()
                else:
                    print("Expected ';'")
            else:
                print("Expected ')'")
        else:
            print("Expected '('")

    def if_stat():
        token = get_token()
        if token == "("):
            token = get_token()
            condition()
            if token == ")"):
                token = get_token()
                if token == ":"):
                    token = get_token()
                    if token == "#{"):
                        statements()
                        if token == "#}"):
                            token = get_token()
                        else:
                            print("Expected '#}'")
                    else:
                        statement()
                    if token == "else"):
                        token = get_token()
                        if token == ":"):
                            token = get_token()
                            if token == "#{"):
                                statements()
                                if token == "#}"):
                                    token = get_token()
                                else:
                                    print("Expected '#}'")
                            else:
                                statement()
                else:
                    print("Expected ':'")
            else:
                print("Expected ')'")
        else:
            print("Expected '('")

    def while_stat():
        token = get_token()
        if token == "("):
            token = get_token()
            condition()
            if token == ")"):
                token = get_token()
                if token == ":"):
                    token = get_token()
                    if token == "#{"):
                        statements()
                        if token == "#}"):
                            token = get_token()
                        else:
                            print("Expected '#}'")
                    else:
                        statement()
                else:
                    print("Expected ':'")
            else:
                print("Expected ')'")
        else:
            print("Expected '('")

    def id_list():
        if token == "ID"):
            token = get_token()
            while (token == ","):
                token = get_token()
                if token == "ID"):
                    token = get_token()
                else:
                    print("Expected a parameter")

    def expression():
        optional_sign()
        term()
        while (token == "+" or token == "-"):
            token = get_token()
            term()

    def term():
        factor()
        while (token == "*" or token == "//"):
            token = get_token()
            factor()

    def factor():
        if token.isnumeric()):
            token = get_token()
        elif token == "("):
            token = get_token()
            expression()
            if token == ")"):
                token = get_token()
            else:
                print("Expected ')'")
        elif token == "ID"):
            token = get_token()
            idtail()
        else:
            print("Expected a factor") # better error?

    def idtail():
        token = get_token()
        if token == "("):
            token = get_token()
            if token == ")"):
                token = get_token()
            else:
                actual_par_list()
                if token == ")"):
                    token = get_token()
                else:
                    print("Expected ')'")

    def actual_par_list():
        expression()
        while (token == ","):
            token = get_token()
            expression()

    def optional_sign():
        if token == "+" or token == "-"):
            token = get_token()
        
    def condition():
        bool_term()
        while (token == "or"):
            token = get_token()
            bool_term()

    def bool_term():
        bool_factor
        while (token == "and"):
            token = get_token()
            bool_factor()

    def bool_factor():
        if token == "not"):
            token = get_token()
            if token == "["):
                token = get_token()
                condition()
                if token == "]"):
                    token = get_token()
                else:
                    print("Expected ']'")
            else:
                print("Expected '['")
        elif token == "["):
            token = get_token()
            condition()
            if token == "]"):
                token = get_token()
            else:
                print("Expected ']'")
        else:
            expression()
            if token == "==" or token == "<" or token == ">"
                or token == "!=" or token == "<="
                or token == ">="):
                token = get_token()
            else:
                print("Expected relational operator")
            expression()

    def call_main_part():
        if token == "if"):
            token = get_token()
            if token == "__name__"):
                token = get_token()
                if token == "=="):
                    token = get_token()
                    if token == "__main__"):
                        token == get_token()
                        if token == ":"):
                            token = get_token()
                            main_function_call()
                            while (token == "ID"):
                                main_function_call()
                        else:
                            print("Expected ':'") # better error?
                    else:
                        print("Expected '__main__'") # better error?
                else:
                    print("Expected '=='") # better error?
            else:
                print("Expected '__name__'") # better error?

        else:
            print("Expected 'if'") # better error?

    def main_function_call():
        if token == "ID"):
            token == get_token()
            if token == "("):
                token = get_token()
                if token == ")"):
                    token = get_token()
                    if token == ";"):
                        token == get_token()
                    else:
                        print("Expected ';'")
                else:
                    print("Expected ')'")
            else:
                print("Expected '('") 
        else:
            print("Expected 'ID'")  # better error?      
    
'''