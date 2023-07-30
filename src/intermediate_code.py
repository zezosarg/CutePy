from symbol_table import TemporaryVariable

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
    def __init__(self, symbol_table):
        self.quads_labels_dict = {}
        self.next_label = 0
        self.cur_temp_number = 0
        self.symbol_table = symbol_table

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
        self.symbol_table.add_record(TemporaryVariable(new_var, "Integer", self.symbol_table.table_list[-1].offset))
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
            for label, quad in self.quads_labels_dict.items():
                file.write(str(label) + ": " + quad.__str__() + "\n")
