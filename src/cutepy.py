from symbol_table import SymbolTable
from intermediate_code import IntCode
from parser import Parser
from final_code import FinalCode
import sys  # for command line arguments

def main():
    # hasReturn = False
    symbol_table = SymbolTable()
    int_code = IntCode(symbol_table)
    s_t = open("symbol_table.txt", "w")
    s_t.close()
    s_t = open("final_code.asm", "w")
    s_t.close()
    parser = Parser(sys.argv[1], symbol_table, int_code)
    # parser = Parser('factorial.cpy', symbol_table, int_code)
    parser.syntax_analyzer()
    final_code = FinalCode(int_code, symbol_table)
    int_code.write_to_file_int()
    final_code.generate_final_code()

if __name__=="__main__":
    main()
