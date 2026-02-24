import os
class Parser:

    def __init__(self, path):
     """
     Initializes a new instace of the parser class, opens the input - source VM code file.
     Args: an instance of the class itself, and the path to the file
     """
     self.vm_code = self.__clean_vm_file(path)
     self.line_number = 0
     self.filename=self.__clean_filename(path)
     self.command_type = None
     self._reset()

    def has_more_commands(self):
        """ 
        has more commands checks if we are done with reading the file or not
        """
        return len(self.vm_code) > 0
    def advance(self):
        """Advance gets the next command and makes it the current instruction (string)
        """
        self.line_number = self.line_number +1
        self._reset()
        code = self.vm_code.pop(0) # pop removes and returns the first index of the dictionary
        self.current_command = code
        self._set_command_Type(code)


    def _reset(self):
           """reset resetes all data
           """
           self.current_command = None
           self.command_type = None
           self.arg1 = None
           self.arg2 = None

    def __clean_vm_file(self,path):
        """Clean vm file gets the path to the file, and simply returns a list of the lines in a clean way - no comments, not spaces
        """

        clean_lines = [] # an empty list that will hold the empty lines
        for line in self.__open_file(path):
            clean_line = self.__remove_whitespace_and_comments(line)
            if clean_line:
                clean_lines.append(clean_line)
        return clean_lines
            
    def __clean_filename(self,path):
        """ Clean file name returns the clean version of the file name 
        """
        return os.path.basename(path).replace('.vm','')
    
    def __open_file(self,path):
        """Open file opens the path file for reading, and returns the vm code
        """
        f = open(path,'r')
        vm_code = f.readlines()
        f.close()
        return vm_code
    
    def __remove_whitespace_and_comments(self,line):
        """ A helper function that cleans a certain line and returns it 
        """
        return line.strip().split("//")[0].strip()
    
    def _set_command_Type(self,command):
        """ Set command types gets a certain command, and returns the type of the command, moreover, it prepares all the information
        about the current command, and stores it in the class attributes, arg1,arg2.
        """
        Arithmetic_commands = ['add','sub','neg','eq','gt','lt','and','or','not'] 
        tokens = command.split() # split the command by spaces
        cmd = tokens[0]

        if cmd in Arithmetic_commands:
            self.command_type = "C_ARITHMETIC"
            self.arg1 = cmd
        elif cmd == "push":
            self.command_type = "C_PUSH"
            self.arg1 = tokens[1]     
            self.arg2 = int(tokens[2]) 
            
        elif cmd == "pop":
            self.command_type = "C_POP"
            self.arg1 = tokens[1]
            self.arg2 = int(tokens[2])

        elif cmd == "label":
            self.command_type = "C_LABEL"
            self.arg1 = tokens[1] 

        elif cmd == "goto":
            self.command_type = "C_GOTO"
            self.arg1 = tokens[1]

        elif cmd == "if-goto":
            self.command_type = "C_IF"
            self.arg1 = tokens[1]

        elif cmd == "function":
            self.command_type = "C_FUNCTION"
            self.arg1 = tokens[1]      # function name
            self.arg2 = int(tokens[2]) # number of locals

        elif cmd == "return":
            self.command_type = "C_RETURN"
            # return has no arguments

        elif cmd == "call":
            self.command_type = "C_CALL"
            self.arg1 = tokens[1]      # function name
            self.arg2 = int(tokens[2]) # number of args