class FinalCode:
    def __init__(self, int_code, symbol_table):
        self.int_code = int_code
        self.symbol_table = symbol_table

    # Search for var in ancestors
    def gnlvcode(self, var):
        record_info = self.recover_record(var)
        level_count = 0
        if record_info == None:
            parser.error("Variable " + var + " was not found in the symbol table.")
        level_count = record_info[1]
        self.write_to_file_final_code("lw t0, -4(sp)")
        for i in range(level_count - 2, 0, -1):
            self.write_to_file_final_code("lw t0, -4(t0)")
        self.write_to_file_final_code("addi t0, t0, -" + str(record_info[0].offset))

    def loadvr(self, reg, v):
        # reg = target, v = source
        if str(v) == "0" or str(v).lstrip("-").isnumeric() and not str(v).lstrip("-").startswith("0"):
            self.write_to_file_final_code("li {target}, {integer}".format(target = reg, integer = v))
        else:
            if str(v).lstrip("-").startswith("0"):
                parser.error("An integer should not start with 0")
            record_info = self.recover_record(v.lstrip("-"))
            if record_info == None:
                parser.error("Variable " + v + " was not found in the symbol table.")
            level_count = record_info[1]
            level_found = record_info[2]
            # Global Case
            if level_found == 0:
                self.write_to_file_final_code("lw {target}, -{offset}(s1)".format(target = reg, offset = record_info[0].offset))

            # Local Case
            elif level_count == 1 :
                self.write_to_file_final_code("lw {target}, -{offset}(sp)".format(target = reg, offset = record_info[0].offset))
            # Ancestor Case
            else:
                self.gnlvcode(v.lstrip("-"))
                self.write_to_file_final_code("lw {target}, 0(t0)".format(target = reg))
            if (v.startswith("-")):
                self.write_to_file_final_code("sub {target}, zero, {target}".format(target = reg))
        


    def storerv(self, v, reg):
        # v = source, reg = target
        if str(reg) == "0" or str(reg).lstrip("-").isnumeric() and not str(reg).lstrip("-").startswith("0"):
            self.loadvr("t0", v)
            self.storerv(v, "t0")
        else:
            if str(reg).lstrip("-").startswith("0"):
                parser.error("An integer should not start with 0")
            record_info = self.recover_record(reg.lstrip("-"))
            if record_info == None:
                parser.error("Variable " + reg + " was not found in the symbol table.")
            level_count = record_info[1]
            level_found = record_info[2]
            if (reg.startswith("-")):
                self.write_to_file_final_code("sub {source}, zero, {source}".format(source = v))
            # Global Case
            if level_found == 0:
                self.write_to_file_final_code("sw {source}, -{offset}(s1)".format(source = v, offset = record_info[0].offset))
            # Local Case
            elif level_count == 1 :
                self.write_to_file_final_code("sw {source}, -{offset}(sp)".format(source = v, offset = record_info[0].offset))
            # Ancestor Case
            else:
                self.gnlvcode(reg.lstrip("-"))
                self.write_to_file_final_code("sw {source}, 0(t0)".format(source = v))
            

    def generate_final_code(self):
        cur_subprogram_name = ""
        pars_count = 0
        table_pos = 0
        is_halt = 0
        par_flag = 0
        self.write_to_file_final_code(".data\n\tbuffer: .space 4\n.text\n.globl main\nmain:")
        self.write_to_file_final_code("j L_{label}".format(label = self.get_next_main(0)))
        for label, quad in self.int_code.quads_labels_dict.items():
            if is_halt == 0:
                self.write_to_file_final_code("L_" + str(label) + ":")
            if quad.operator == "jump":
                self.write_to_file_final_code("j L_" + str(quad.target))
            elif quad.operator == "halt":
                next_main_label = self.get_next_main(label)
                if next_main_label != None:
                    self.write_to_file_final_code("j L_{label}".format(label = next_main_label))
                else:
                    self.write_to_file_final_code("li a7, 93")
                    # Status code 0 indicates success
                    self.write_to_file_final_code("li a0, 0")
                    self.write_to_file_final_code("ecall")
                is_halt = 1
                table_pos = 0
            elif quad.operator == "begin_block":
                cur_subprogram_name = quad.operant1
                self.symbol_table.table_list = self.symbol_table.table_list_container[table_pos]
                self.write_to_file_final_code("L_{function}:".format(function = cur_subprogram_name))
                if cur_subprogram_name.startswith("main"):
                    subprogram_scope = self.symbol_table.table_list[0]
                    self.write_to_file_final_code("addi sp, sp, {framelength}".format(framelength = subprogram_scope.offset))
                    self.write_to_file_final_code("mv s1, sp")
                else:
                    self.write_to_file_final_code("sw ra, -0(sp)")
            elif quad.operator == "end_block":
                if is_halt == 0:
                    self.write_to_file_final_code("lw ra, -0(sp)")
                    self.write_to_file_final_code("jr ra")
                par_flag = 0
                is_halt = 0
                del self.symbol_table.table_list_container[table_pos]
            elif quad.operator == "+": 
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("add t1, t1, t2")
                self.storerv("t1", quad.target)
            elif quad.operator == "*":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("mul t1, t1, t2")
                self.storerv("t1", quad.target)
            elif quad.operator == "//":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("div t1, t1, t2")
                self.storerv("t1", quad.target)
            elif quad.operator == "-":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("sub t1, t1, t2")
                self.storerv("t1", quad.target)
            elif quad.operator == "<":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("blt t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == ">":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("bgt t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == "<=":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("ble t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == ">=":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("bge t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == "==":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("beq t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == "!=":
                self.loadvr("t1", quad.operant1)
                self.loadvr("t2", quad.operant2)
                self.write_to_file_final_code("bne t1, t2, L_{dest}".format(dest = quad.target))
            elif quad.operator == "in":
                self.write_to_file_final_code("la a0, buffer")
                self.write_to_file_final_code("li a7, 5")
                self.write_to_file_final_code("ecall")
                self.storerv("a0", quad.operant1)
            elif quad.operator == "out":
                self.write_to_file_final_code("li a7, 1")
                self.loadvr("a0", quad.operant1)
                self.write_to_file_final_code("ecall")
                # print newline
                self.write_to_file_final_code("li a7, 11")
                self.write_to_file_final_code("li a0, '{newline}'".format(newline = "\\n"))
                self.write_to_file_final_code("ecall")
            elif quad.operator == "ret": 
                self.loadvr("t1", quad.target)
                self.write_to_file_final_code("lw t0, -8(sp)")
                self.write_to_file_final_code("sw t1, 0(t0)")
                self.write_to_file_final_code("j L_{end_block}".format(end_block = self.get_next_end_block(label)))
            elif quad.operator == "par" and quad.operant2 == "cv":
                callee_name = self.get_callee_name(label)
                callee = self.recover_record(callee_name)[0]
                if par_flag == 0:
                    self.write_to_file_final_code("addi fp, sp, {framelength}".format(framelength = callee.framelength))
                    par_flag = 1
                self.loadvr("t0", quad.operant1)
                self.write_to_file_final_code("sw t0, -{offset}(fp)".format(offset = 12 + (4 * pars_count)))
                pars_count += 1
            elif quad.operator == "par" and quad.operant2 == "ret":
                # Subprogram.framelength must find the new_var in symbol table
                ret_var = self.recover_record(quad.operant1)[0]
                self.write_to_file_final_code("addi t0, sp, -{offset}".format(offset = ret_var.offset))
                self.write_to_file_final_code("sw t0, -8(fp)")
            elif quad.operator == "call":
                par_flag = 0
                pars_count = 0
                caller = self.recover_record(cur_subprogram_name)
                callee = self.recover_record(quad.operant1)
                caller_level = 0
                if not cur_subprogram_name.startswith("main"):
                    caller_level = caller[1]
                callee_level = callee[1]
                # Same parent case
                if caller_level == callee_level:
                    self.write_to_file_final_code("lw t0, -4(sp)")
                    self.write_to_file_final_code("sw t0, -4(fp)")
                # Different parent case
                else:
                    self.write_to_file_final_code("sw sp, -4(fp)")
                self.write_to_file_final_code("addi sp, sp, {framelength}".format(framelength = callee[0].framelength))
                self.write_to_file_final_code("jal L_{function}".format(function = callee[0].name))
                self.write_to_file_final_code("addi sp, sp, -{framelength}".format(framelength = callee[0].framelength))
            elif quad.operator == "=":
                self.loadvr("t1", quad.operant1)
                self.storerv("t1", quad.target)   


    def get_callee_name(self, current_label):
        dict = self.int_code.quads_labels_dict
        cur_quad = dict[current_label]
        while cur_quad.operator != "call":
            current_label += 1
            cur_quad = dict[current_label]
        return cur_quad.operant1

    def get_next_main(self, current_label):
        dict = self.int_code.quads_labels_dict
        dict_length = len(dict)
        cur_quad = dict[current_label]
        while not cur_quad.operant1.startswith("main") or not cur_quad.operator == "begin_block":
            current_label += 1
            if current_label == dict_length:
                return None
            cur_quad = dict[current_label]
        return current_label

    def get_next_end_block(self, current_label):
        dict = self.int_code.quads_labels_dict
        dict_length = len(dict)
        cur_quad = dict[current_label]
        while not cur_quad.operator == "end_block":
            current_label += 1
            if current_label == dict_length:
                return None
            cur_quad = dict[current_label]
        return current_label

    def recover_record(self, record_name):
        table_container = self.symbol_table.table_list_container
        cpy_cur_list = self.symbol_table.table_list.copy()
        record = None
        for list in table_container:
            self.symbol_table.table_list = list
            record = self.symbol_table.get_record(record_name)
            if record != None:
                self.symbol_table.table_list = cpy_cur_list
                return record
        self.symbol_table.table_list = cpy_cur_list
    
    def write_to_file_final_code(self, instruction):
        file_name = "final_code.asm"
        # Open the file in append mode
        with open(file_name, "a") as file:
            if instruction.startswith("L_") or instruction.startswith("."):
                file.write(instruction + "\n")
            else:
                file.write("\t" + instruction + "\n")
