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
