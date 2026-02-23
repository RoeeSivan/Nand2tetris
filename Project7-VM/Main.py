import sys
import os
from Parser import Parser
from CodeWriter import CodeWriter

def main():
    # 1. Get the input path from command line args
    input_path = sys.argv[1]
    
    # List to hold all the .vm files we need to process
    vm_files = []
    
    # 2. Check if the input is a directory or a file
    if os.path.isdir(input_path):
        # Directory case
        # Get the actual folder name to name the output file (e.g., "dir" from "path/to/dir")
        # os.path.normpath removes trailing slashes which can confuse os.path.basename
        dir_name = os.path.basename(os.path.normpath(input_path))
        output_path = os.path.join(input_path, dir_name + ".asm")
        
        # Collect all .vm files in this directory
        for filename in os.listdir(input_path):
            if filename.endswith(".vm"):
                full_path = os.path.join(input_path, filename)
                vm_files.append(full_path)
    else:
        # --- SINGLE FILE CASE ---
        output_path = input_path.replace(".vm", ".asm")
        vm_files.append(input_path)

    # 3. Initialize CodeWriter (Only ONE output file is created regardless of input type)
    writer = CodeWriter(output_path)
    
    # 4. Loop through all collected .vm files
    for vm_file in vm_files:
        parser = Parser(vm_file)
        
        # Tell the writer which file we are translating now.
        # This ensures static variables (e.g., @FileName.i) are named correctly per file.
        writer.setFileName(parser.filename) 

        while parser.has_more_commands():
            parser.advance()
            c_type = parser.command_type
            
            if c_type == "C_ARITHMETIC":
                writer.writeArithmetic(parser.arg1)
            elif c_type == "C_PUSH" or c_type == "C_POP":
                writer.WritePushPop(c_type, parser.arg1, parser.arg2)
                
    # 5. Close the output file when done
    writer.close()

if __name__ == "__main__":
    main()