from cpy_lex import Lex

lex = Lex("factorial.cpy")
token = lex.next_token()

while token.family != "error" and token.family != "eof":
    print(token)
    token = lex.next_token()

del lex
