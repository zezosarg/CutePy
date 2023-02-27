from token import Token

class Lex:

    #this is called a destructor apparently
    #def __del__():

    def __init__(self, current_line, file_name, token):
        self.current_line = current_line
        self.file_name = file_name
        self.token = token

    #def error():

    #def next_token():
    