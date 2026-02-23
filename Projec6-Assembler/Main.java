import java.io.File;
import java.io.IOException;
import java.io.FileWriter;

public class Main {

    public static void main(String[] args) {
        Code coder = new Code();

        // Check if args exist to avoid crash if no file provided
        if (args.length == 0) {
            System.out.println("No source file specified.");
            return;
        }
        String sourcename = args[0];
        File sourceFile = new File(sourcename);
        String outputName = sourcename.replace(".asm", ".hack");

        try (FileWriter writer = new FileWriter(outputName)) {


            SymbolTable table = new SymbolTable();
            Parser p = new Parser(sourceFile);
            int romAddress = 0;

            // --- FIRST PASS ---
            while (p.hasMoreLines()) {
                try {
                    p.advance();
                    if (p.Instructiontype().equals("L_INSTRUCTION")) {
                        table.addEntry(p.symbol(), romAddress);
                    } else {
                        romAddress++;
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }

            // --- SECOND PASS ---
            Parser p2 = new Parser(sourceFile);
            int variableAddress = 16; 
            int addressValue = 0;

            // manage newlines - if 
            boolean isFirstLine = true;

            while (p2.hasMoreLines()) {
                try {
                    p2.advance();

                    if (p2.Instructiontype().equals("L_INSTRUCTION")) {
                        continue;
                    }

                    String binary = ""; // we will store the result here first

                    if (p2.Instructiontype().equals("A_INSTRUCTION")) {
                        try {
                            addressValue = Integer.parseInt(p2.symbol());
                        } catch (NumberFormatException e) {
                            if (table.contains(p2.symbol())) {
                                addressValue = table.getAddress(p2.symbol());
                            } else {
                                // Use variableAddress (starts at 16) for variables
                                table.addEntry(p2.symbol(), variableAddress);
                                addressValue = variableAddress;
                                variableAddress++;
                            }
                        }
                        // Format to 16-bit binary
                        binary = Integer.toBinaryString(0x10000 | addressValue).substring(1);

                    } else { // C_INSTRUCTION
                        String comp = p2.comp();
                        String dest = p2.dest();
                        String jump = p2.jump();

                        String cBits = coder.comp(comp);
                        String dBits = coder.dest(dest);
                        String jBits = coder.jump(jump);

                        binary = "111" + cBits + dBits + jBits; //final result
                    }

                    // 
                    // Only write a newline if this is NOT the first line.
                    if (!isFirstLine) {
                        writer.write("\n");
                    }

                    writer.write(binary);

                    // After we write the first line, we set this to false
                    isFirstLine = false;

                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}