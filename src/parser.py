from lexical_analyser import Token, Lex
from symbol_table import SymbolTable, Variable, Function, Parameter
from intermediate_code import IntCode, Quad
import re

class Parser:
    def __init__(self, file_name, symbol_table, int_code):
        self.lexical_analyser = Lex(file_name)
        self.symbol_table = symbol_table
        self.int_code = int_code

    def syntax_analyzer(self):
        global token
        token = self.get_token()
        self.start_rule()
        print('compilation successfully completed')

    def get_token(self):
        next_token = self.lexical_analyser.next_token()
        print("token:", next_token)
        return next_token

    def error(self, description="no description"):
        print("Error:", description, " at line:", token.line_number,
              " token.recognized_string:", token.recognized_string)
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
            # Starts with "main_" and has at least one letter or digit after
            if token.family == "identifier" and re.search("^main_[a-zA-Z0-9]+", token.recognized_string):
                self.symbol_table.add_level()
                function_name = token.recognized_string
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
                                self.int_code.genQuad("begin_block", function_name, "_", "_")
                                self.statements()
                                self.int_code.genQuad("halt", "_", "_", "_")
                                self.int_code.genQuad("end_block", function_name, "_", "_")
                                self.symbol_table.write_to_file_symbol()
                                self.symbol_table.remove_level()
                                if token.recognized_string == "#}":
                                    token = self.get_token()
                                else:
                                    self.error(
                                        "Expected '#}' in def_main_function")
                            else:
                                self.error(
                                    "Expected '#{' in def_main_function")
                        else:
                            self.error("Expected ':' in def_main_function")
                    else:
                        self.error("Expected ')' in def_main_function")
                else:
                    self.error("Expected '(' in def_main_function")
            else:
                self.error(
                    "Expected identifier that starts with 'main_' in def_main_function")
        else:
            self.error("Expected keyword 'def' in def_main_function")

    def def_function(self):
        global token, hasReturn
        # Does not start with "main_"
        if token.family == "identifier" and re.search("^(?!main_)", token.recognized_string):
            function_name = token.recognized_string
            self.symbol_table.add_record(Function(function_name, None, "Integer", [], 0))
            self.symbol_table.add_level()
            token = self.get_token()
            if token.recognized_string == "(":
                token = self.get_token()
                param_list = self.id_list()
                for param in param_list:
                    self.symbol_table.add_record(Parameter(param, "Integer", "cv", self.symbol_table.table_list[-1].offset))
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
                            self.int_code.genQuad("begin_block", function_name, "_", "_")
                            first_label = self.int_code.nextQuad()
                            self.statements()
                            self.symbol_table.write_to_file_symbol()
                            self.symbol_table.update_fields(function_name, self.symbol_table.table_list[-1].offset, self.int_code.getQuadByLabel(first_label), param_list)
                            if not hasReturn:
                                self.error("Expected return statement in local function")
                            hasReturn = False
                            self.int_code.genQuad("end_block", function_name, "_", "_")
                            self.symbol_table.remove_level()
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
            param_list = self.id_list()
            for param in param_list:
                self.symbol_table.add_record(Variable(param, "Integer", self.symbol_table.table_list[-1].offset))
        else:
            self.error(
                "Expected 'declare' keyword after '#' in declaration_line")

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
        global hasReturn
        if token.recognized_string == "print":
            source = self.print_stat()
            self.int_code.genQuad("out", source, "_", "_")
        elif token.recognized_string == "return":
            target = self.return_stat()
            hasReturn = True
            self.int_code.genQuad("ret", "_", "_", target)
        elif token.family == "identifier":
            target = token.recognized_string
            a_temp = self.assignment_stat()
            self.int_code.genQuad("=", a_temp, "_", target)
        else:
            self.error(
                "Expected 'print', 'return' or identifier in simple_statement")

    def structured_statement(self):
        if token.recognized_string == "if":
            self.if_stat()
        elif token.recognized_string == "while":
            self.while_stat()
        else:
            self.error("Expected 'if' or 'while' in structured_statement")

    def assignment_stat(self):
        global token
        a_temp = ""
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
                                        a_temp = self.int_code.newTemp()
                                        self.int_code.genQuad("in", a_temp, "_", "_")
                                        token = self.get_token()
                                    else:
                                        self.error(
                                            "Expected ';' in assignment_stat")
                                else:
                                    self.error(
                                        "Expected ')' in assignment_stat")
                            else:
                                self.error("Expected ')' in assignment_stat")
                        else:
                            self.error("Expected '(' in assignment_stat")
                    else:
                        self.error("Expected 'input' in assignment_stat")
                else:
                    self.error("Expected '(' in assignment_stat")
            else:
                a_temp = self.expression()
                if token.recognized_string == ";":
                    token = self.get_token()
                else:
                    self.error("Expected ';' in assignment_stat")
        else:
            self.error("Expected '=' in assignment_stat")
        return a_temp

    def print_stat(self):
        global token
        token = self.get_token()
        if token.recognized_string == "(":
            token = self.get_token()
            e_place = self.expression()
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
        return e_place

    def return_stat(self):
        global token
        token = self.get_token()
        if token.recognized_string == "(":
            token = self.get_token()
            e_place = self.expression()
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
        return e_place;

    def if_stat(self):
        global token
        token = self.get_token()
        if token.recognized_string == "(":
            token = self.get_token()
            c_arr = self.condition()
            c_true = c_arr[0]
            c_false = c_arr[1]
            if token.recognized_string == ")":
                token = self.get_token()
                if token.recognized_string == ":":
                    token = self.get_token()
                    self.int_code.backpatch(c_true,self.int_code.nextQuad())
                    if token.recognized_string == "#{":
                        token = self.get_token()
                        self.statements()
                        if token.recognized_string == "#}":
                            token = self.get_token()
                        else:
                            self.error("Expected '#}' in if_stat")
                    else:
                        self.statement()
                    if_list = self.int_code.makeList(Quad("jump", "_", "_", "_"))
                    # ELSE PART
                    if token.recognized_string == "else":
                        self.int_code.backpatch(c_false,self.int_code.nextQuad()+1)
                        self.int_code.genQuad("jump","_","_","_")
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
                    self.int_code.backpatch(c_false,self.int_code.nextQuad())
                    self.int_code.backpatch(if_list, self.int_code.nextQuad())
                else:
                    self.error("Expected ':' in if_stat")
            else:
                self.error("Expected ')' in if_stat")
        else:
            self.error("Expected '(' in if_stat")

    def while_stat(self):
        global token
        token = self.get_token()
        condQuad = self.int_code.nextQuad()
        if token.recognized_string == "(":
            token = self.get_token()
            c_arr = self.condition()
            c_true = c_arr[0]
            c_false = c_arr[1]
            if token.recognized_string == ")":
                token = self.get_token()
                self.int_code.backpatch(c_true, self.int_code.nextQuad())
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
                    self.int_code.genQuad("jump", "_", "_", condQuad)
                    self.int_code.backpatch(c_false, self.int_code.nextQuad())
                else:
                    self.error("Expected ':' in while_stat")
            else:
                self.error("Expected ')' in while_stat")
        else:
            self.error("Expected '(' in while_stat")

    def id_list(self):
        global token
        param_list = []
        if token.family == "identifier":
            param_list.append(token.recognized_string)
            token = self.get_token()
            while token.recognized_string == ",":
                token = self.get_token()
                if token.family == "identifier":
                    param_list.append(token.recognized_string)
                    token = self.get_token()
                else:
                    self.error("Expected an identifier in id_list")
        return param_list

    def expression(self):
        global token
        sign = self.optional_sign()
        if sign == "-":
            t1_place = sign + self.term()
        else:
            t1_place = self.term()
        while token.recognized_string == "+" or token.recognized_string == "-":
            operator = token.recognized_string
            token = self.get_token()
            t2_place = self.term()
            w = self.int_code.newTemp()
            self.int_code.genQuad(operator, t1_place, t2_place, w)
            t1_place = w
        return t1_place

    def term(self):
        global token
        f1_place = self.factor()
        while token.recognized_string == "*" or token.recognized_string == "//":
            operator = token.recognized_string 
            token = self.get_token()
            f2_place = self.factor()
            w = self.int_code.newTemp()
            self.int_code.genQuad(operator, f1_place, f2_place, w)
            f1_place = w
        return f1_place



    def factor(self):
        global token
        if token.recognized_string.isnumeric():
            f_place = token.recognized_string
            token = self.get_token()
        elif token.recognized_string == "(":
            token = self.get_token()
            f_place = self.expression()
            if token.recognized_string == ")":
                token = self.get_token()
            else:
                self.error("Expected ')' in factor")
        elif token.family == "identifier" and re.search("^(?!main_)", token.recognized_string):
            f_place = token.recognized_string
            token = self.get_token()
            ret_var = self.idtail()
            if ret_var != None:
                self.int_code.genQuad("call", f_place, "_", "_")
                f_place = ret_var
        else:
            self.error(
                "Expected integer or expression or non main identifier in factor")
        return f_place

    def idtail(self):
        global token
        new_var = None
        if token.recognized_string == "(":
            token = self.get_token()
            new_var = self.actual_par_list()
            self.int_code.genQuad("par", new_var, "ret", "_")
            if token.recognized_string == ")":
                token = self.get_token()
            else:
                self.error("Expected ')' in idtail")        
        return new_var

    def actual_par_list(self):
        global token
        t_list = []
        param1 = self.expression()
        t_list.append(param1);
        while token.recognized_string == ",":
            token = self.get_token()
            param2 = self.expression()
            t_list.append(param2)
        for param in t_list:
             #-- CREATE RECORDS FOR FORMAL PARAMS
            self.int_code.genQuad("par", param, "cv", "_")
        return self.int_code.newTemp()

    def optional_sign(self):
        global token
        sign = None
        if token.recognized_string == "+" or token.recognized_string == "-":
            sign = token.recognized_string
            token = self.get_token()
        return sign


    def condition(self):
        global token
        q1_arr = self.bool_term()
        b_true = q1_arr[0] 
        b_false = q1_arr[1] 
        while token.recognized_string == "or":
            token = self.get_token()
            self.int_code.backpatch(b_false, self.int_code.nextQuad()) 
            q2_arr = self.bool_term()
            q2_true = q2_arr[0]
            q2_false = q2_arr[1]
            b_true = self.int_code.mergeList(b_true, q2_true)
            b_false = q2_false
        return [b_true, b_false]

    def bool_term(self):
        global token
        r1_arr = self.bool_factor()
        q_true = r1_arr[0]
        q_false = r1_arr[1]
        while token.recognized_string == "and":
            token = self.get_token()
            self.int_code.backpatch(q_true, self.int_code.nextQuad())
            r2_arr = self.bool_factor()
            r2_true = r2_arr[0]
            r2_false = r2_arr[1]
            q_false = self.int_code.mergeList(q_false, r2_false)
            q_true = r2_true
        return [q_true, q_false]

    def bool_factor(self):
        global token
        r_true = []
        r_false = []
        if token.recognized_string == "not":
            token = self.get_token()
            if token.recognized_string == "[":
                token = self.get_token()
                b_arr = self.condition()
                if token.recognized_string == "]":
                    token = self.get_token()
                    r_true = b_arr[1]
                    r_false = b_arr[0]
                else:
                    self.error("Expected ']' in bool_factor")
            else:
                self.error("Expected '[' in bool_factor")
        elif token.recognized_string == "[":
            token = self.get_token()
            b_arr = self.condition()
            if token.recognized_string == "]":
                token = self.get_token()
                r_true = b_arr[0]
                r_false = b_arr[1]
            else:
                self.error("Expected ']' in bool_factor")
        else:
            e1_place = self.expression()
            rel_op = ""
            if token.recognized_string in ["==", "<", ">", ">=", "<=", "!="]:
                rel_op = token.recognized_string
                token = self.get_token()
            else:
                self.error("Expected relational operator in bool_factor")
            e2_place = self.expression()
            self.int_code.genQuad(rel_op, e1_place, e2_place, "_")
            r_true = self.int_code.makeList(Quad(rel_op, e1_place, e2_place, "_"))
            nl = str(self.int_code.next_label)
            self.int_code.genQuad("jump", "_", "_", "c_" + nl)
            r_false = self.int_code.makeList(Quad("jump", "_", "_", "c_" + nl))
        return [r_true, r_false]

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
                                    self.error(
                                        "Expected ':' in call_main_part")
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
    