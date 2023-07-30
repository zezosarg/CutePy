import sys
sys.path.insert(1, '../src')
from parser import Parser

parser = Parser("factorial.cpy")

parser.syntax_analyzer()