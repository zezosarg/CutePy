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
        file_name = "symbol_table.txt"
        # Open the file in write mode
        with open(file_name, "a") as file:
            for scope in reversed(self.table_list):
                file.write("level " + str(scope.level) + " <-- ")
                for record in scope.record_list:
                    if record.name == scope.record_list[-1].name:
                        file.write(record.__str__())
                    else:
                        file.write(record.__str__() + " <-- ")
                file.write("\n")
            file.write("-----------------------------------------------------------------------------" + "\n")
