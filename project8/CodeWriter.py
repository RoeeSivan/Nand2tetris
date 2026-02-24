import textwrap

class CodeWriter:
    def __init__(self, path):
        """opens an output file and gets ready to write into it"""
        self.output_file = open(path, 'w')
        self.label_counter = 0
        self.file_name = ""

    def setFileName(self, fileName):
        """informs the code writer that the translation of a new vm file is starting"""
        self.file_name = fileName

    def writeArithmetic(self, command):
        """Write to the output file the assembly code that implements the given arithmetic command"""
        code = ""
        if command == "add":
            code = self.__add_command()
        elif command == "sub":
            code = self.__sub_command()
        elif command == "neg":
            code = self.__neg_command()
        elif command == "eq":
            code = self.__eq_command()
        elif command == "gt":
            code = self.__gt_command()
        elif command == "lt":
            code = self.__lt_command()
        elif command == "and":
            code = self.__and_command()
        elif command == "or":
            code = self.__or_command()
        elif command == "not":
            code = self.__not_command()

        if code:
            # We add a newline at the end for clean separation between commands
            self.output_file.write(code + "\n")

    def WritePushPop(self, command, segment, index):
        code = ""
        segment_pointers = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        fixed_segments = {"temp": 5, "pointer": 3}

        if command == "C_PUSH":
            if segment == "constant":
                # We dedent this specific block immediately
                part1 = textwrap.dedent(f"""\
                    @{index}
                    D=A
                    """)
                code = part1 + self.__push_d_to_stack()
                
            elif segment in segment_pointers:
                pointer = segment_pointers[segment]
                part1 = textwrap.dedent(f"""\
                    @{index}
                    D=A
                    @{pointer}
                    A=M
                    A=D+A
                    D=M
                    """)
                code = part1 + self.__push_d_to_stack()

            elif segment in fixed_segments:
                base_addr = fixed_segments[segment]
                part1 = textwrap.dedent(f"""\
                    @{base_addr}
                    D=A
                    @{index}
                    A=D+A
                    D=M
                    """)
                code = part1 + self.__push_d_to_stack()

            elif segment == "static":
                static_label = f"{self.file_name}.{index}"
                part1 = textwrap.dedent(f"""\
                    @{static_label}
                    D=M
                    """)
                code = part1 + self.__push_d_to_stack()

        elif command == "C_POP":
            if segment in segment_pointers:
                pointer = segment_pointers[segment]
                code = textwrap.dedent(f"""\
                    @{index}
                    D=A
                    @{pointer}
                    A=M
                    D=D+A
                    @R13
                    M=D
                    @SP
                    AM=M-1
                    D=M
                    @R13
                    A=M
                    M=D
                    """)
            elif segment in fixed_segments:
                base_addr = fixed_segments[segment]
                code = textwrap.dedent(f"""\
                    @{base_addr}
                    D=A
                    @{index}
                    D=D+A
                    @R13
                    M=D
                    @SP
                    AM=M-1
                    D=M
                    @R13
                    A=M
                    M=D
                    """)
            elif segment == "static":
                static_label = f"{self.file_name}.{index}"
                code = textwrap.dedent(f"""\
                    @SP
                    AM=M-1
                    D=M
                    @{static_label}
                    M=D
                    """)

        if code:
            # .strip() removes empty lines at start/end, then we add exactly one newline
            self.output_file.write(code.strip() + "\n")
            #all these methods below get a label string, writefunction andwritecall get also an int
    def writeLabel(self,label): 
            self.output_file.write(f"({label})\n")
    def writeGoto(self,label):
                code = textwrap.dedent(f"""\
                    @{label}
                    0;JMP
                    """)
                if code:
                 self.output_file.write(code.strip() + "\n")
                               
    def writeIf(self,label):
                code = textwrap.dedent(f"""\
                    @SP
                    AM=M-1
                    D=M
                    @{label}
                    D;JNE                   
                    """)
                if code:
                 self.output_file.write(code.strip() + "\n")
    def writeFunction(self, functionName, numLocals):
        # 1. Write the function label
        self.output_file.write(f"({functionName})\n")
        
        # 2. Initialize D to 0
        self.output_file.write(textwrap.dedent("""\
            @0
            D=A
            """))
        # 3. Push 0 to the stack 'numLocals' times
        for _ in range(numLocals):
             self.output_file.write(self.__push_d_to_stack())


    def writeCall(self, functionName, numArgs):
        return_label = f"{functionName}$ret.{self.label_counter}"
        self.label_counter += 1
        
        # 1. Push return address
        code = textwrap.dedent(f"""\
            @{return_label}
            D=A
            """)
        code += self.__push_d_to_stack()
        
        # 2. Push LCL, ARG, THIS, THAT
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            code += textwrap.dedent(f"""\
                @{segment}
                D=M
                """)
            code += self.__push_d_to_stack()
            
        # 3. Reposition ARG = SP - n - 5
        code += textwrap.dedent(f"""\
            @SP
            D=M
            @{numArgs}
            D=D-A
            @5
            D=D-A
            @ARG
            M=D
            """)
            
        # 4. Reposition LCL = SP
        code += textwrap.dedent("""\
            @SP
            D=M
            @LCL
            M=D
            """)
            
        # 5. Goto function
        code += textwrap.dedent(f"""\
            @{functionName}
            0;JMP
            """)
            
        # 6. Declare return label
        code += f"({return_label})\n"
        
        self.output_file.write(code)

                
    def writeReturn(self):
         # frame = LCL, (we save LCL to R13)
         code = ""
         code += textwrap.dedent(f"""\
            @LCL
            D=M
            @R13
            M=D
            """)
         # we save the return addres to R14
         code += textwrap.dedent(f"""\
            @5
            A=D-A
            D=M
            @R14
            M=D
            """)
         # we put the return value where the caller expects it 
         code += textwrap.dedent(f"""\
            @SP
            AM=M-1
            D=M
            @ARG
            A=M
            M=D
            """)
         # we do SP = ARG+1 
         code += textwrap.dedent(f"""\
            @ARG
            D=M+1
            @SP
            M=D
            """)
         # now we restore That, this,args,lcl
         for offset, segment in enumerate(["THAT","THIS","ARG","LCL"], start =1):
              code += textwrap.dedent(f"""\
            @R13
            D=M
            @{offset}
            A=D-A
            D=M
            @{segment}
            M=D
            """)
        # we jump to the saved return address
         code += textwrap.dedent("""  
         @R14
         A=M
         0;JMP
         """)
         self.output_file.write(code.strip() + "\n")                        
                                 
                                                  
                            
    def close(self):
        self.output_file.close()

    def __push_d_to_stack(self):
        """Returns a clean, unindented block for pushing D to stack"""
        return textwrap.dedent("""\
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """)

    # --- Arithmetic Helpers: ALL return clean, dedented strings ---

    def __add_command(self):
        return textwrap.dedent("""\
            @SP
            AM=M-1
            D=M
            A=A-1
            M=D+M
            """)

    def __sub_command(self):
        return textwrap.dedent("""\
            @SP
            AM=M-1
            D=M
            A=A-1
            M=M-D
            """)

    def __neg_command(self):
        return textwrap.dedent("""\
            @SP
            A=M-1
            M=-M
            """)

    def __not_command(self):
        return textwrap.dedent("""\
            @SP
            A=M-1
            M=!M
            """)

    def __eq_command(self):
        label_true = f"TRUE_{self.label_counter}"
        label_end = f"END_{self.label_counter}"
        self.label_counter += 1
        return textwrap.dedent(f"""\
            @SP
            AM=M-1
            D=M
            A=A-1
            D=M-D
            @{label_true}
            D;JEQ
            @SP
            A=M-1
            M=0
            @{label_end}
            0;JMP
            ({label_true})
            @SP
            A=M-1
            M=-1
            ({label_end})
            """)

    def __gt_command(self):
        label_true = f"TRUE_{self.label_counter}"
        label_end = f"END_{self.label_counter}"
        self.label_counter += 1
        return textwrap.dedent(f"""\
            @SP
            AM=M-1
            D=M
            A=A-1
            D=M-D
            @{label_true}
            D;JGT
            @SP
            A=M-1
            M=0
            @{label_end}
            0;JMP
            ({label_true})
            @SP
            A=M-1
            M=-1
            ({label_end})
            """)

    def __lt_command(self):
        label_true = f"TRUE_{self.label_counter}"
        label_end = f"END_{self.label_counter}"
        self.label_counter += 1
        return textwrap.dedent(f"""\
            @SP
            AM=M-1
            D=M
            A=A-1
            D=M-D
            @{label_true}
            D;JLT
            @SP
            A=M-1
            M=0
            @{label_end}
            0;JMP
            ({label_true})
            @SP
            A=M-1
            M=-1
            ({label_end})
            """)

    def __and_command(self):
        return textwrap.dedent("""\
            @SP
            M=M-1
            A=M
            D=M
            A=A-1
            M=D&M
            """)

    def __or_command(self):
        return textwrap.dedent("""\
            @SP
            M=M-1
            A=M
            D=M
            A=A-1
            M=D|M
            """)
    def writeInit(self):
          code = textwrap.dedent("""\
                                 @256
                                 D=A
                                 @SP
                                 M=D
                                 """)
          self.output_file.write(code)
          self.writeCall("Sys.init", 0)