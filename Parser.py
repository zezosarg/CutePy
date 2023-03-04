token = ""

def lex():  # Prepei na prostethei o lektikos analytis
    return "" 

def start_rule():
    def_main_part()
    call_main_part()


def def_main_part():
    def_main_function()
    while (token == "def"):
        def_main_function()


def def_main_function():
    if (token == "ID"):  # ID is a valid function name, maybe with regex
        token = lex()
        if (token == "("):
            token = lex()
            if (token == ")"):
                token = lex()
                if (token == ":"):
                    token = lex()
                    if (token == "#{"):
                        token = lex()
                        declarations()
                        while (token == "def"):
                            def_function()
                        statements()
                        if (token == "#}"):
                            token = lex()
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


def def_function():
    if (token == "ID"):
        token = lex()
        if (token == "("):
            token = lex()
            id_list()
            if (token == ")"):
                token = lex()
                if (token == ":"):
                    token = lex()
                    if (token == "#{"):
                        token = lex()
                        declarations()
                        while (token == "def"):
                            def_function()
                        statements()
                        if (token == "#}"):
                            token = lex()
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
    token = lex()
    id_list()


def statement():
    if (token == "if" or token == "while"):
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
    if (token == "ID"):
        assignment_stat()
    elif (token == "print"):
        print_stat()
    elif (token == "return"):
        return_stat()
    else:
        print("Token doesn't exist")


def structured_statement():
    if (token == "if"):
        if_stat()
    elif (token == "while"):
        while_stat()
    else:
        print("Token doesn't exist")


def assignment_stat():  # Oi parentheseis paizoyn kapoio rolo sthn grammatiki?
    token = lex()
    if (token == "="):
        token = lex()
        if (token == "int"):
            token = lex()
            if (token == "("):
                token = lex()
                if (token == "input"):
                    token = lex()
                    if (token == "("):
                        token = lex()
                        if (token == ")"):
                            token = lex()
                            if (token == ")"):
                                token = lex()
                                if (token == ";"):
                                    token = lex()
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
            if (token == ";"):
                token = lex()
            else:
                print("Expected ';'")
    else:
        print("Expected '='")


def print_stat():
    token = lex()
    if (token == "("):
        token = lex()
        expression()
        if (token == ")"):
            token = lex()
            if (token == ";"):
                token = lex()
            else:
                print("Expected ';'")
        else:
            print("Expected ')'")
    else:
        print("Expected '('")

def return_stat():
    token = lex()
    if (token == "("):
        token = lex()
        expression()
        if (token == ")"):
            token = lex()
            if (token == ";"):
                token = lex()
            else:
                print("Expected ';'")
        else:
            print("Expected ')'")
    else:
        print("Expected '('")

def if_stat():
    token = lex()
    if (token == "("):
        token = lex()
        condition()
        if (token == ")"):
            token = lex()
            if (token == ":"):
                token = lex()
                if (token == "#{"):
                    statements()
                    if (token == "#}"):
                        token = lex()
                    else:
                        print("Expected '#}'")
                else:
                    statement()
                if (token == "else"):
                    token = lex()
                    if (token == ":"):
                        token = lex()
                        if (token == "#{"):
                            statements()
                            if (token == "#}"):
                                token = lex()
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
    token = lex()
    if (token == "("):
        token = lex()
        condition()
        if (token == ")"):
            token = lex()
            if (token == ":"):
                token = lex()
                if (token == "#{"):
                    statements()
                    if (token == "#}"):
                        token = lex()
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
    if (token == "ID"):
        token = lex()
        while (token == ","):
            token = lex()
            if (token == "ID"):
                token = lex()
            else:
                print("Expected a parameter")

def expression():
    optional_sign()
    term()
    while (token == "+" or token == "-"):
        token = lex()
        term()

def term():
    factor()
    while (token == "*" or token == "//"):
        token = lex()
        factor()

def factor():
    if (token.isnumeric()):
        token = lex()
    elif (token == "("):
        token = lex()
        expression()
        if (token == ")"):
            token = lex()
        else:
            print("Expected ')'")
    elif (token == "ID"):
        token = lex()
        idtail()
    else:
        print("Expected a factor") # better error?

def idtail():
    token = lex()
    if (token == "("):
        token = lex()
        if (token == ")"):
            token = lex()
        else:
            actual_par_list()
            if (token == ")"):
                token = lex()
            else:
                print("Expected ')'")

def actual_par_list():
    expression()
    while (token == ","):
        token = lex()
        expression()

def optional_sign():
    if (token == "+" or token == "-"):
        token = lex()
    
def condition():
    bool_term()
    while (token == "or"):
        token = lex()
        bool_term()

def bool_term():
    bool_factor
    while (token == "and"):
        token = lex()
        bool_factor()

def bool_factor():
    if (token == "not"):
        token = lex()
        if (token == "["):
            token = lex()
            condition()
            if (token == "]"):
                token = lex()
            else:
                print("Expected ']'")
        else:
            print("Expected '['")
    elif (token == "["):
        token = lex()
        condition()
        if (token == "]"):
            token = lex()
        else:
            print("Expected ']'")
    else:
        expression()
        if (token == "==" or token == "<" or token == ">"
            or token == "!=" or token == "<="
            or token == ">="):
            token = lex()
        else:
            print("Expected relational operator")
        expression()

def call_main_part():
    if (token == "if"):
        token = lex()
        if (token == "__name__"):
            token = lex()
            if (token == "=="):
                token = lex()
                if (token == "__main__"):
                    token == lex()
                    if (token == ":"):
                        token = lex()
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
    if (token == "ID"):
        token == lex()
        if (token == "("):
            token = lex()
            if (token == ")"):
                token = lex()
                if (token == ";"):
                    token == lex()
                else:
                    print("Expected ';'")
            else:
                print("Expected ')'")
        else:
            print("Expected '('") 
    else:
        print("Expected 'ID'")  # better error?      