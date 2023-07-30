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
                #-- CREATE NEW LEVEL 
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
                                genQuad("begin_block", function_name, "_", "_")
                                self.statements()
                                genQuad("halt", "_", "_", "_")
                                genQuad("end_block", function_name, "_", "_")
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
        global token
        # Does not start with "main_"
        if token.family == "identifier" and re.search("^(?!main_)", token.recognized_string):
            function_name = token.recognized_string
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
                            genQuad("begin_block", function_name, "_", "_")
                            self.statements()
                            genQuad("end_block", function_name, "_", "_")
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
        if token.recognized_string == "print":
            source = self.print_stat()
            genQuad("out", source, "_", "_")
        elif token.recognized_string == "return":
            target = self.return_stat()
            genQuad("ret", "_", "_", target)
        elif token.family == "identifier":
            target = token.recognized_string
            a_temp = self.assignment_stat()
            genQuad("=", a_temp, "_", target)

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
                                        a_temp = newTemp()
                                        genQuad("in", a_temp, "_", "_")
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
                    backpatch(c_true,nextQuad())
                    if token.recognized_string == "#{":
                        token = self.get_token()
                        self.statements()
                        if token.recognized_string == "#}":
                            token = self.get_token()
                        else:
                            self.error("Expected '#}' in if_stat")
                    else:
                        self.statement()
                    if_list = makeList(Quad("jump", "_", "_", "_"))
                    # ELSE PART
                    if token.recognized_string == "else":
                        backpatch(c_false,nextQuad()+1)
                        genQuad("jump","_","_","_")
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
                    backpatch(if_list, nextQuad())
                else:
                    self.error("Expected ':' in if_stat")
            else:
                self.error("Expected ')' in if_stat")
        else:
            self.error("Expected '(' in if_stat")

    def while_stat(self):
        global token
        token = self.get_token()
        condQuad = nextQuad()
        if token.recognized_string == "(":
            token = self.get_token()
            c_arr = self.condition()
            c_true = c_arr[0]
            c_false = c_arr[1]
            if token.recognized_string == ")":
                token = self.get_token()
                backpatch(c_true, nextQuad())
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
                    genQuad("jump", "_", "_", condQuad)
                    backpatch(c_false, nextQuad())
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
        sign = self.optional_sign()
        if sign == "-":
            t1_place = sign + self.term()
        else:
            t1_place = self.term()
        while token.recognized_string == "+" or token.recognized_string == "-":
            operator = token.recognized_string
            token = self.get_token()
            t2_place = self.term()
            w = newTemp()
            genQuad(operator, t1_place, t2_place, w)
            t1_place = w
        return t1_place

    def term(self):
        global token
        f1_place = self.factor()
        while token.recognized_string == "*" or token.recognized_string == "//":
            operator = token.recognized_string 
            token = self.get_token()
            f2_place = self.factor()
            w = newTemp()
            genQuad(operator, f1_place, f2_place, w)
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
                genQuad("call", f_place, "_", "_")
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
            genQuad("par", new_var, "ret", "_")
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
            genQuad("par", param, "cv", "_")
        return newTemp()

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
            backpatch(b_false, nextQuad()) 
            q2_arr = self.bool_term()
            q2_true = q2_arr[0]
            q2_false = q2_arr[1]
            b_true = mergeList(b_true, q2_true)
            b_false = q2_false
        return [b_true, b_false]

    def bool_term(self):
        global token
        r1_arr = self.bool_factor()
        q_true = r1_arr[0]
        q_false = r1_arr[1]
        while token.recognized_string == "and":
            token = self.get_token()
            backpatch(q_true, nextQuad())
            r2_arr = self.bool_factor()
            r2_true = r2_arr[0]
            r2_false = r2_arr[1]
            q_false = mergeList(q_false, r2_false)
            q_true = r2_true
        return [q_true, q_false]

    def bool_factor(self):
        global token, not_flag
        r_true = []
        r_false = []
        if token.recognized_string == "not":
            token = self.get_token()
            if token.recognized_string == "[":
                token = self.get_token()
                not_flag = 1
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
                if not_flag == 1:
                    rel_op = get_reverse_op(rel_op)
                    not_flag = 0
                token = self.get_token()
            else:
                self.error("Expected relational operator in bool_factor")
            e2_place = self.expression()
            genQuad(rel_op, e1_place, e2_place, "_")
            r_true = makeList(Quad(rel_op, e1_place, e2_place, "_"))
            genQuad("jump", "_", "_", "_")
            r_false = makeList(Quad("jump", "_", "_", "_"))
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
next_label = 0
quads_labels_dict = {}
cur_temp_number = 0


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

    
def genQuad(operator, operant1, operant2, target):
    global next_label, quads_labels_dict
    next_quad = Quad(operator, operant1, operant2, target)
    quads_labels_dict[next_label] = next_quad
    next_label += 1
    return next_quad


def nextQuad():
    return next_label


def emptyList():
    return []


def makeList(label):
    return [label]


def mergeList(l1, l2):
    return l1 + l2


def newTemp():
    global cur_temp_number
    new_var = "T_" + str(cur_temp_number)
    cur_temp_number += 1
    return new_var


def backpatch(list, new_label):
    global quads_labels_dict
    for cmp_quad in list:
        for label, quad in quads_labels_dict.items():
            if quad.__equals__(cmp_quad):
                quad.target = new_label



def write_to_file():
    global quads_labels_dict
    # Define the file path and name
    file_name = "IntCode"
    # Open the file in write mode
    with open(file_name, "w") as file:
        # Write the dictionary to the file
        for label, quad in quads_labels_dict.items():
            file.write(str(label) + ": " + quad.__str__() + "\n")

def get_reverse_op(op):
    if op == "<":
        return ">="
    elif op == ">":
        return "<="
    elif op == "==":
        return "!="
    elif op == "!=":
        return "=="
    elif op == "<=":
        return ">"
    else:
        return "<"

class Entity:
    def __init__(self, name):
        self.name = name


class Variable(Entity):
    def __init__(self, name, datatype, offset):
        super().__init__(name)                      
        self.datatype = datatype                    
        self.offset = offset                        

    def __str__(self):
        return (str(self.name) + ", " + str(self.datatype) + ", " + str(self.offset))


class Subprogram(Entity):
    def __init__(self, name, startingQuad, formalParameters, framelength):
        super().__init__(name)                      
        self.startingQuad = startingQuad            
        self.formalParameters = formalParameters    
        self.framelength = framelength              # activation record length 


class Procedure(Subprogram):
        def __init__(self, name, startingQuad, formalParameters, framelength):
            super().__init__(name, startingQuad, formalParameters, framelength)

        def __str__(self):
            return str(self.name) + ", " + str(self.startingQuad) + ", "  + str(self.framelength)

class Function(Subprogram):
        def __init__(self, name, startingQuad, datatype, formalParameters, framelength):
            super().__init__(name, startingQuad, formalParameters, framelength)
            self.datatype = datatype

        def __str__(self):
            return str(self.name) + ", " + str(self.startingQuad) + ", " + str(self.datatype) + ", " + str(self.framelength)


class FormalParameter(Entity):
    def __init__(self, name, offset, datatype, mode):
        super().__init__(name)
        self.offset = offset
        self.datatype = datatype
        self.mode = mode

    def __str__(self):
        return str(self.name) + ", " + str(self.datatype) + ", " + str(self.offset) + ", " + str(self.mode)


class TemporaryVariable(Variable):
    def __init__(self, name, datatype, offset):
        super().__init__(name, datatype, offset)

class Parameter(FormalParameter):
        def __init__(self, name, datatype, mode, offset):
            super().__init__(name, datatype, mode)  # parameter's ID
            self.offset = offset

class SymbolicConstant(Entity):
    def __init__(self, name, datatype, value):
        super().__init__(name)
        self.datatype = datatype
        self.value = value

class Scope:
    def __init__(self, level):
        self.record_list = []
        self.level = level
        self.offset = 12

    def __str__(self):

        return "Level: " + str(self.level) + ", " + str(self.offset)


class SymbolTable:
    def __init__(self):
        # List contains Scope objects
        self.table_list = []

    def add_record(self, record):
        self.table_list[-1].record_list.append(record)
        self.table_list[-1].offset += 4

    def add_level(self):
        cur_level = self.table_list.len()
        self.table_list.append(Scope(cur_level))

    def remove_level(self):
        self.table_list.pop()

    # For Subprograms and children classes
    #Needs checking
    def update_fields(self, frame_length, starting_quad):
        records = self.table_list[-1].record_list
        for record in records:
            if isinstance(record, Subprogram):
                record.framelength = frame_length
                record.startingQuad = starting_quad
  
    def add_formal_parameter(self, parameter):
        records = self.table_list[-1].record_list
        for record in records:
            if isinstance(record, Subprogram):
                record.formalParameters.append(parameter)

    def get_record(self, record_name):
        for record_list in reversed(self.table_list):
            for record in record_list:
                if record.name == record_name:
                    return record;
        return None

not_flag = 0
parser = Parser(sys.argv[1])
symbol_table = SymbolTable()
#parser = Parser("test1.cpy")
parser.syntax_analyzer()
write_to_file()
