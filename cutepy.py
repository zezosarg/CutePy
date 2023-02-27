from token import Token
from lex import Lex

def main():
    print("Hello World!")
    token = Token("a", "b", 3)
    print(token)
    lex = Lex(1, "lol.cpy", token)
    print(lex)

if __name__ == "__main__":
    main()
