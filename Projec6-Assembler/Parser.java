import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class Parser {
    private BufferedReader reader;
    public String currentCommand;
    public String nextLine;

    public Parser(File file) {
        try {
            reader = new BufferedReader(new FileReader(file));
            currentCommand = null;
            // We "prime" the nextLine immediately with the first VALID
            // command
            nextLine = getNextValidLine();
        } catch (IOException e) {
            System.out.print("Error reading file: " + file.getAbsolutePath());
            e.printStackTrace();
        }
    }

    public boolean hasMoreLines() {
        return (nextLine != null);
    }

    public void advance() throws IOException {
        //simple shift. Current becomes Next, and we fetch a new Next.
        currentCommand = nextLine;
        nextLine = getNextValidLine();
    }

    // This does the heavy lifting of skipping
    // comments/whitespace
    private String getNextValidLine() throws IOException {
        String line;
        while ((line = reader.readLine()) != null) {
            // 1. Remove comments
            int commentIndex = line.indexOf("//");
            if (commentIndex != -1) {
                line = line.substring(0, commentIndex);
            }

            // 2. Trim whitespace
            line = line.trim();

            // 3. If line is not empty, we found a command!
            if (!line.isEmpty()) {
                return line;
            }
            // If empty, the loop continues to read the next line
        }
        return null; // Reached End of File without finding a command
    }

    public String Instructiontype() {
        if (currentCommand.startsWith("@")) {
            return "A_INSTRUCTION";
        }
        if (currentCommand.startsWith("(") && (currentCommand.endsWith(")"))) {
            return "L_INSTRUCTION";
        }
        return "C_INSTRUCTION";
    }

    public String symbol() {
        if (Instructiontype().equals("A_INSTRUCTION")) {
            return currentCommand.substring(1);
        }
        if (Instructiontype().equals("L_INSTRUCTION")) {
            return currentCommand.substring(1, currentCommand.length() - 1);
        }
        return "";
    }

    public String dest() {
        if (Instructiontype().equals("C_INSTRUCTION")) {
            if (currentCommand.contains("=")) {
                return currentCommand.substring(0, currentCommand.indexOf("="));
            }
        }
        return null;
    }

    public String comp() {
        if (Instructiontype().equals("C_INSTRUCTION")) {
            int eqIndex = currentCommand.indexOf("=");
            int semiIndex = currentCommand.indexOf(";");

            if (eqIndex != -1) { // dest=comp...
                if (semiIndex != -1) {
                    // dest=comp;jump
                    return currentCommand.substring(eqIndex + 1, semiIndex);
                } else {
                    // dest=comp
                    return currentCommand.substring(eqIndex + 1);
                }
            } else { // comp;jump
                if (semiIndex != -1) {
                    return currentCommand.substring(0, semiIndex);
                }
            }
        }
        return null;
    }

    public String jump() {
        if (Instructiontype().equals("C_INSTRUCTION")) {
            if (currentCommand.contains(";")) {
                return currentCommand.substring(currentCommand.indexOf(";") + 1);
            }
        }
        return null;
    }
}