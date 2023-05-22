# Argyrios Zezos, 4588, cse84588
# Fotios Pappas, 4773, cse94773

import re   # regular expressions
import sys  # for command line arguments

hasReturn = False

class Token:

    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __str__(self):
        return str(self.recognized_string) + '\tfamily:\"' + str(self.family) + '\",\tline: ' + str(self.line_number)


class Lex:
    def __init__(self, file_name, file_pointer=None, current_line=1):
        self.file_name = file_name
        self.file_pointer = open(file_name, "r")
        self.current_line = current_line

    def __del__(self):
        self.file_pointer.close()

    def error(self, description="no description"):
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
                keywords = ["not", "and", "or", "if", "else", "while",
                            "return", "print", "def", "int", "input", "declare"]
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
                symbol_table.add_level()
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
                                int_code.genQuad("begin_block", function_name, "_", "_")
                                self.statements()
                                int_code.genQuad("halt", "_", "_", "_")
                                int_code.genQuad("end_block", function_name, "_", "_")
                                symbol_table.write_to_file_symbol()
                                symbol_table.remove_level()
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
            symbol_table.add_record(Function(function_name, None, "Integer", [], 0))
            symbol_table.add_level()
            token = self.get_token()
            if token.recognized_string == "(":
                token = self.get_token()
                param_list = self.id_list()
                for param in param_list:
                    symbol_table.add_record(Parameter(param, "Integer", "cv", symbol_table.table_list[-1].offset))
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
                            int_code.genQuad("begin_block", function_name, "_", "_")
                            first_label = int_code.nextQuad()
                            self.statements()
                            symbol_table.write_to_file_symbol()
                            symbol_table.update_fields(function_name, symbol_table.table_list[-1].offset, int_code.getQuadByLabel(first_label), param_list)
                            if not hasReturn:
                                self.error("Expected return statement in local function")
                            hasReturn = False
                            int_code.genQuad("end_block", function_name, "_", "_")
                            symbol_table.remove_level()
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
                symbol_table.add_record(Variable(param, "Integer", symbol_table.table_list[-1].offset))
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
            int_code.genQuad("out", source, "_", "_")
        elif token.recognized_string == "return":
            target = self.return_stat()
            hasReturn = True
            int_code.genQuad("ret", "_", "_", target)
        elif token.family == "identifier":
            target = token.recognized_string
            a_temp = self.assignment_stat()
            int_code.genQuad("=", a_temp, "_", target)
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
                                        a_temp = int_code.newTemp()
                                        int_code.genQuad("in", a_temp, "_", "_")
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
                    int_code.backpatch(c_true,int_code.nextQuad())
                    if token.recognized_string == "#{":
                        token = self.get_token()
                        self.statements()
                        if token.recognized_string == "#}":
                            token = self.get_token()
                        else:
                            self.error("Expected '#}' in if_stat")
                    else:
                        self.statement()
                    if_list = int_code.makeList(Quad("jump", "_", "_", "_"))
                    # ELSE PART
                    if token.recognized_string == "else":
                        int_code.backpatch(c_false,int_code.nextQuad()+1)
                        int_code.genQuad("jump","_","_","_")
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
                    int_code.backpatch(c_false,int_code.nextQuad())
                    int_code.backpatch(if_list, int_code.nextQuad())
                else:
                    self.error("Expected ':' in if_stat")
            else:
                self.error("Expected ')' in if_stat")
        else:
            self.error("Expected '(' in if_stat")

    def while_stat(self):
        global token
        token = self.get_token()
        condQuad = int_code.nextQuad()
        if token.recognized_string == "(":
            token = self.get_token()
            c_arr = self.condition()
            c_true = c_arr[0]
            c_false = c_arr[1]
            if token.recognized_string == ")":
                token = self.get_token()
                int_code.backpatch(c_true, int_code.nextQuad())
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
                    int_code.genQuad("jump", "_", "_", condQuad)
                    int_code.backpatch(c_false, int_code.nextQuad())
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
            w = int_code.newTemp()
            int_code.genQuad(operator, t1_place, t2_place, w)
            t1_place = w
        return t1_place

    def term(self):
        global token
        f1_place = self.factor()
        while token.recognized_string == "*" or token.recognized_string == "//":
            operator = token.recognized_string 
            token = self.get_token()
            f2_place = self.factor()
            w = int_code.newTemp()
            int_code.genQuad(operator, f1_place, f2_place, w)
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
                int_code.genQuad("call", f_place, "_", "_")
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
            int_code.genQuad("par", new_var, "ret", "_")
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
            int_code.genQuad("par", param, "cv", "_")
        return int_code.newTemp()

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
            int_code.backpatch(b_false, int_code.nextQuad()) 
            q2_arr = self.bool_term()
            q2_true = q2_arr[0]
            q2_false = q2_arr[1]
            b_true = int_code.mergeList(b_true, q2_true)
            b_false = q2_false
        return [b_true, b_false]

    def bool_term(self):
        global token
        r1_arr = self.bool_factor()
        q_true = r1_arr[0]
        q_false = r1_arr[1]
        while token.recognized_string == "and":
            token = self.get_token()
            int_code.backpatch(q_true, int_code.nextQuad())
            r2_arr = self.bool_factor()
            r2_true = r2_arr[0]
            r2_false = r2_arr[1]
            q_false = int_code.mergeList(q_false, r2_false)
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
            int_code.genQuad(rel_op, e1_place, e2_place, "_")
            r_true = int_code.makeList(Quad(rel_op, e1_place, e2_place, "_"))
            nl = str(int_code.next_label)
            int_code.genQuad("jump", "_", "_", "c_" + nl)
            r_false = int_code.makeList(Quad("jump", "_", "_", "c_" + nl))
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
    
# INTERMIDIATE CODE

class Quad:
    def __init__(self, operator, operant1, operant2, target):
        self.operator = operator
        self.operant1 = operant1
        self.operant2 = operant2
        self.target = target

    def __str__(self):
        return (str(self.operator)) + "," + (str(self.operant1)) + "," + (str(self.operant2)) + "," + (str(self.target))
    
    def __equals__(self, another_quad):
        if (self.operator == another_quad.operator and 
            self.operant1 == another_quad.operant1 and 
            self.operant2 == another_quad.operant2 and 
            self.target == another_quad.target):
            return True
        return False

class IntCode:
    def __init__(self):
        self.quads_labels_dict = {}
        self.next_label = 0
        self.cur_temp_number = 0

    def genQuad(self, operator, operant1, operant2, target):
        next_quad = Quad(operator, operant1, operant2, target)
        self.quads_labels_dict[self.next_label] = next_quad
        self.next_label += 1
        return next_quad


    def nextQuad(self):
        return self.next_label


    def emptyList(self):
        return []


    def makeList(self, label):
        return [label]


    def mergeList(self, l1, l2):
        return l1 + l2


    def newTemp(self):
        new_var = "%" + str(self.cur_temp_number)
        self.cur_temp_number += 1
        symbol_table.add_record(TemporaryVariable(new_var, "Integer", symbol_table.table_list[-1].offset))
        return new_var


    def backpatch(self, list, new_label):
        for cmp_quad in list:
            for label, quad in self.quads_labels_dict.items():
                if quad.__equals__(cmp_quad):
                    quad.target = new_label

    def getQuadByLabel(self, label):
        return self.quads_labels_dict.get(label)

    def write_to_file_int(self):
        # Define the file path and name
        file_name = "code.int"
        # Open the file in write mode
        with open(file_name, "w") as file:
            # Write the dictionary to the file
            for label, quad in int_code.quads_labels_dict.items():
                file.write(str(label) + ": " + quad.__str__() + "\n")
    
    # SYMBOL TABLE 

class Entity:
    def __init__(self, name: str):
        self.name = name


class Variable(Entity):
    def __init__(self, name, datatype, offset):
        super().__init__(name)                      
        self.datatype = datatype                    
        self.offset = offset                        

    def __str__(self):
        return (str(self.name) + "/" + str(self.offset))


class Subprogram(Entity):
    def __init__(self, name, startingQuad, formalParameters, framelength):
        super().__init__(name)                      
        self.startingQuad = startingQuad            
        self.formalParameters = formalParameters    
        self.framelength = framelength              


class Function(Subprogram):
        def __init__(self, name, startingQuad, datatype, formalParameters, framelength):
            super().__init__(name, startingQuad, formalParameters, framelength)
            self.datatype = datatype

        def __str__(self):
            if self.framelength != 0:
                return str(self.name) + "/" + str(self.framelength)
            else:
                return str(self.name)


class FormalParameter(Entity):
    def __init__(self, name, datatype, mode):
        super().__init__(name)
        self.datatype = datatype
        self.mode = mode

    def __str__(self):
        return str(self.name) + "/"  + str(self.offset) + "/" + str(self.mode)


class TemporaryVariable(Variable):
    def __init__(self, name, datatype, offset):
        super().__init__(name, datatype, offset)

class Parameter(FormalParameter):
        def __init__(self, name, datatype, mode, offset):
            super().__init__(name, datatype, mode)  
            self.offset = offset

class Scope:
    def __init__(self, level):
        self.record_list = []
        self.level = level
        self.offset = 12

class SymbolTable:
    def __init__(self):
        # List contains Scope objects
        self.table_list = []
        self.table_list_container = []

    def add_record(self, record):
        self.table_list[-1].record_list.append(record)
        if not isinstance(record, Subprogram):
            self.table_list[-1].offset += 4

    def add_level(self):
        cur_level = len(self.table_list)
        self.table_list.append(Scope(cur_level))

    def remove_level(self):
        self.table_list_container.append(self.table_list.copy())
        self.table_list.pop()
        
    def update_fields(self, subprogram_name, frame_length, starting_quad, formal_parameters):
        if len(self.table_list) > 1:
            records = self.table_list[-2].record_list
        else:
            records = self.table_list[-1].record_list
        for record in records:
            if isinstance(record, Subprogram) and record.name == subprogram_name:
                record.framelength = frame_length
                record.startingQuad = starting_quad
                record.formalParameters = formal_parameters
  
    def add_formal_parameter(self, parameter):
        records = self.table_list[-1].record_list
        for record in records:
            if isinstance(record, Subprogram):
                record.formalParameters.append(parameter)

    def get_record(self, record_name):
        level_count = 0
        for scope in reversed(self.table_list):
            level_count += 1
            for record in scope.record_list:
                if record.name == record_name:
                    return [record, level_count, scope.level];
        return None
    
    def write_to_file_symbol(self):
        # Define the file path and name
        file_name = "symbol_table"
        # Open the file in write mode
        with open(file_name, "a") as file:
            for scope in reversed(symbol_table.table_list):
                file.write("level " + str(scope.level) + " <-- ")
                for record in scope.record_list:
                    if record.name == scope.record_list[-1].name:
                        file.write(record.__str__())
                    else:
                        file.write(record.__str__() + " <-- ")
                file.write("\n")
            file.write("-----------------------------------------------------------------------------" + "\n")
    
class FinalCode:
    # Search for var in ancestors
    def gnlvcode(self, var):
        record_info = final_code.recover_record(var)
        level_count = 0
        if record_info == None:
            parser.error("Variable " + var + " was not found in the symbol table.")
        level_count = record_info[1]
        final_code.write_to_file_final_code("lw t0, -4(sp)")
        for i in range(level_count - 2, 0, -1):
            final_code.write_to_file_final_code("lw t0, -4(t0)")
        final_code.write_to_file_final_code("addi t0, t0, -" + str(record_info[0].offset))

    def loadvr(self, reg, v):
        # reg = target, v = source
        if str(v) == "0" or str(v).lstrip("-").isnumeric() and not str(v).lstrip("-").startswith("0"):
            final_code.write_to_file_final_code("li {target}, {integer}".format(target = reg, integer = v))
        else:
            if str(v).lstrip("-").startswith("0"):
                parser.error("An integer should not start with 0")
            record_info = final_code.recover_record(v.lstrip("-"))
            if record_info == None:
                parser.error("Variable " + v + " was not found in the symbol table.")
            level_count = record_info[1]
            level_found = record_info[2]
            # Global Case
            if level_found == 0:
                final_code.write_to_file_final_code("lw {target}, -{offset}(s1)".format(target = reg, offset = record_info[0].offset))

            # Local Case
            elif level_count == 1 :
                final_code.write_to_file_final_code("lw {target}, -{offset}(sp)".format(target = reg, offset = record_info[0].offset))
            # Ancestor Case
            else:
                self.gnlvcode(v.lstrip("-"))
                final_code.write_to_file_final_code("lw {target}, 0(t0)".format(target = reg))
            if (v.startswith("-")):
                final_code.write_to_file_final_code("sub {target}, zero, {target}".format(target = reg))
        


    def storerv(self, v, reg):
        # v = source, reg = target
        if str(reg) == "0" or str(reg).lstrip("-").isnumeric() and not str(reg).lstrip("-").startswith("0"):
            self.loadvr("t0", v)
            self.storerv(v, "t0")
        else:
            if str(reg).lstrip("-").startswith("0"):
                parser.error("An integer should not start with 0")
            record_info = final_code.recover_record(reg.lstrip("-"))
            if record_info == None:
                parser.error("Variable " + reg + " was not found in the symbol table.")
            level_count = record_info[1]
            level_found = record_info[2]
            if (reg.startswith("-")):
                final_code.write_to_file_final_code("sub {source}, zero, {source}".format(source = v))
            # Global Case
            if level_found == 0:
                final_code.write_to_file_final_code("sw {source}, -{offset}(s1)".format(source = v, offset = record_info[0].offset))
            # Local Case
            elif level_count == 1 :
                final_code.write_to_file_final_code("sw {source}, -{offset}(sp)".format(source = v, offset = record_info[0].offset))
            # Ancestor Case
            else:
                self.gnlvcode(reg.lstrip("-"))
                final_code.write_to_file_final_code("sw {source}, 0(t0)".format(source = v))
            

    def generate_final_code(self):
        cur_subprogram_name = ""
        pars_count = 0
        table_pos = 0
        is_halt = 0
        par_flag = 0
        final_code.write_to_file_final_code(".data\n\tbuffer: .space 4\n.text\n.globl main\nmain:")
        final_code.write_to_file_final_code("j L_{label}".format(label = final_code.get_next_main(0)))
        for label, quad in int_code.quads_labels_dict.items():
            if is_halt == 0:
                final_code.write_to_file_final_code("L_" + str(label) + ":")
            if quad.operator == "jump":
                final_code.write_to_file_final_code("j L_" + str(quad.target))
            elif quad.operator == "halt":
                next_main_label = final_code.get_next_main(label)
                if next_main_label != None:
                    final_code.write_to_file_final_code("j L_{label}".format(label = next_main_label))
                else:
                    final_code.write_to_file_final_code("li a7, 93")
                    # Status code 0 indicates success
                    final_code.write_to_file_final_code("li a0, 0")
                    final_code.write_to_file_final_code("ecall")
                is_halt = 1
                table_pos = 0
            elif quad.operator == "begin_block":
                cur_subprogram_name = quad.operant1
                symbol_table.table_list = symbol_table.table_list_container[table_pos]
                final_code.write_to_file_final_code("L_{function}:".format(function = cur_subprogram_name))
                if cur_subprogram_name.startswith("main"):
                    subprogram_scope = symbol_table.table_list[0]
                    final_code.write_to_file_final_code("addi sp, sp, {framelength}".format(framelength = subprogram_scope.offset))
                    final_code.write_to_file_final_code("mv s1, sp")
                else:
                    final_code.write_to_file_final_code("sw ra, -0(sp)")
            elif quad.operator == "end_block":
                if is_halt == 0:
                    final_code.write_to_file_final_code("lw ra, -0(sp)")
                    final_code.write_to_file_final_code("jr ra")
                par_flag = 0
                is_halt = 0
                del symbol_table.table_list_container[table_pos]
            elif quad.operator == "+": 
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("add t1, t1, t2")
                self.storerv("t1", quad.target)
            elif quad.operator == "*":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("mul t1, t1, t2")
                self.storerv("t1", quad.target)
            elif quad.operator == "//":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("div t1, t1, t2")
                self.storerv("t1", quad.target)
            elif quad.operator == "-":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("sub t1, t1, t2")
                self.storerv("t1", quad.target)
            elif quad.operator == "<":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("blt t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == ">":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("bgt t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == "<=":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("ble t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == ">=":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("bge t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == "==":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("beq t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == "!=":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                final_code.write_to_file_final_code("bne t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == "in":
                final_code.write_to_file_final_code("la a0, buffer")
                final_code.write_to_file_final_code("li a7, 5")
                final_code.write_to_file_final_code("ecall")
                self.storerv("a0", quad.operant1)
            elif quad.operator == "out":
                final_code.write_to_file_final_code("li a7, 1")
                self.loadvr("a0", quad.operant1)
                final_code.write_to_file_final_code("ecall")
                # print newline
                final_code.write_to_file_final_code("li a7, 11")
                final_code.write_to_file_final_code("li a0, '{newline}'".format(newline = "\\n"))
                final_code.write_to_file_final_code("ecall")
            elif quad.operator == "ret": 
                self.loadvr("t1", quad.target)
                final_code.write_to_file_final_code("lw t0, -8(sp)")
                final_code.write_to_file_final_code("sw t1, 0(t0)")
                final_code.write_to_file_final_code("j L_{end_block}".format(end_block = final_code.get_next_end_block(label)))
            elif quad.operator == "par" and quad.operant2 == "cv":
                callee_name = final_code.get_callee_name(label)
                callee = final_code.recover_record(callee_name)[0]
                if par_flag == 0:
                    final_code.write_to_file_final_code("addi fp, sp, {framelength}".format(framelength = callee.framelength))
                    par_flag = 1
                self.loadvr("t0", quad.operant1)
                final_code.write_to_file_final_code("sw t0, -{offset}(fp)".format(offset = 12 + (4 * pars_count)))
                pars_count += 1
            elif quad.operator == "par" and quad.operant2 == "ret":
                # Subprogram.framelength must find the new_var in symbol table
                ret_var = final_code.recover_record(quad.operant1)[0]
                final_code.write_to_file_final_code("addi t0, sp, -{offset}".format(offset = ret_var.offset))
                final_code.write_to_file_final_code("sw t0, -8(fp)")
            elif quad.operator == "call":
                par_flag = 0
                pars_count = 0
                caller = final_code.recover_record(cur_subprogram_name)
                callee = final_code.recover_record(quad.operant1)
                caller_level = 0
                if not cur_subprogram_name.startswith("main"):
                    caller_level = caller[1]
                callee_level = callee[1]
                # Same parent case
                if caller_level == callee_level:
                    final_code.write_to_file_final_code("lw t0, -4(sp)")
                    final_code.write_to_file_final_code("sw t0, -4(fp)")
                # Different parent case
                else:
                    final_code.write_to_file_final_code("sw sp, -4(fp)")
                final_code.write_to_file_final_code("addi sp, sp, {framelength}".format(framelength = callee[0].framelength))
                final_code.write_to_file_final_code("jal L_{function}".format(function = callee[0].name))
                final_code.write_to_file_final_code("addi sp, sp, -{framelength}".format(framelength = callee[0].framelength))
            elif quad.operator == "=":
                self.loadvr("t1", quad.operant1)
                self.storerv("t1", quad.target)   


    def get_callee_name(self, current_label):
        dict = int_code.quads_labels_dict
        cur_quad = dict[current_label]
        while cur_quad.operator != "call":
            current_label += 1
            cur_quad = dict[current_label]
        return cur_quad.operant1

    def get_next_main(self, current_label):
        dict = int_code.quads_labels_dict
        dict_length = len(dict)
        cur_quad = dict[current_label]
        while not cur_quad.operant1.startswith("main") or not cur_quad.operator == "begin_block":
            current_label += 1
            if current_label == dict_length:
                return None
            cur_quad = dict[current_label]
        return current_label

    def get_next_end_block(self, current_label):
        dict = int_code.quads_labels_dict
        dict_length = len(dict)
        cur_quad = dict[current_label]
        while not cur_quad.operator == "end_block":
            current_label += 1
            if current_label == dict_length:
                return None
            cur_quad = dict[current_label]
        return current_label

    def recover_record(self, record_name):
        table_container = symbol_table.table_list_container
        cpy_cur_list = symbol_table.table_list.copy()
        record = None
        for list in table_container:
            symbol_table.table_list = list
            record = symbol_table.get_record(record_name)
            if record != None:
                symbol_table.table_list = cpy_cur_list
                return record
        symbol_table.table_list = cpy_cur_list
    
    def write_to_file_final_code(self, instruction):
        file_name = "final_code.asm"
        # Open the file in append mode
        with open(file_name, "a") as file:
            if instruction.startswith("L_") or instruction.startswith("."):
                file.write(instruction + "\n")
            else:
                file.write("\t" + instruction + "\n")


symbol_table = SymbolTable()
int_code = IntCode()
s_t = open("symbol_table", "w")
s_t.close()
s_t = open("final_code.asm", "w")
s_t.close()
#parser = Parser(sys.argv[1])
parser = Parser("tests/test.cpy")
parser.syntax_analyzer()
final_code = FinalCode()
int_code.write_to_file_int()
final_code.generate_final_code()

