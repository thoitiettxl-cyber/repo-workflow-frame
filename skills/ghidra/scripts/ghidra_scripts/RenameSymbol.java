/* ###
 * Rename a symbol (function, data label, or code label) at an address.
 * If the address is inside a function, the function is renamed.
 * Otherwise the symbol at the address is renamed (or a new label is created).
 * @category Modify
 */

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

public class RenameSymbol extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            println("Usage: RenameSymbol.java <address> <newName>");
            println("  Example: RenameSymbol.java 0x00123456 my_func");
            println("  If <address> is inside a function, the function is renamed;");
            println("  otherwise the symbol at <address> is renamed (label created if none).");
            return;
        }

        String addrStr = args[0];
        String newName = args[1];

        Address addr;
        try {
            addr = currentProgram.getAddressFactory().getAddress(addrStr);
        } catch (Exception e) {
            println("ERROR: invalid address '" + addrStr + "': " + e.getMessage());
            return;
        }

        String outputDir = System.getenv("GHIDRA_OUTPUT_DIR");
        if (outputDir == null || outputDir.isEmpty()) {
            outputDir = ".";
        }

        String programName = currentProgram.getName().replaceAll("[^a-zA-Z0-9._-]", "_");
        File outputFile = new File(outputDir, programName + "_rename.json");

        FunctionManager funcMgr = currentProgram.getFunctionManager();
        SymbolTable symTable = currentProgram.getSymbolTable();

        String kind;
        String oldName;
        String status = "ok";
        String error = "";

        try {
            Function func = funcMgr.getFunctionContaining(addr);
            if (func != null) {
                // Address lies inside a function -> rename the function itself.
                oldName = func.getName();
                func.setName(newName, SourceType.USER_DEFINED);
                kind = "function";
                println("Renamed function '" + oldName + "' -> '" + newName
                        + "' (entry " + func.getEntryPoint() + ")");
            } else {
                Symbol sym = symTable.getPrimarySymbol(addr);
                if (sym != null) {
                    oldName = sym.getName();
                    String symType = sym.getSymbolType().toString();
                    sym.setName(newName, SourceType.USER_DEFINED);
                    kind = "symbol:" + symType;
                    println("Renamed symbol '" + oldName + "' -> '" + newName
                            + "' (" + symType + ") at " + addr);
                } else {
                    symTable.createLabel(addr, newName, SourceType.USER_DEFINED);
                    oldName = "";
                    kind = "label:created";
                    println("Created label '" + newName + "' at " + addr);
                }
            }
        } catch (ghidra.util.exception.DuplicateNameException e) {
            status = "error";
            kind = "";
            oldName = "";
            error = "duplicate name: " + e.getMessage();
            println("ERROR: name '" + newName + "' already exists: " + e.getMessage());
        } catch (ghidra.util.exception.InvalidInputException e) {
            status = "error";
            kind = "";
            oldName = "";
            error = "invalid name: " + e.getMessage();
            println("ERROR: invalid name '" + newName + "': " + e.getMessage());
        }

        try (PrintWriter writer = new PrintWriter(new FileWriter(outputFile))) {
            writer.println("{");
            writer.println("  \"program\": \"" + escapeJson(currentProgram.getName()) + "\",");
            writer.println("  \"address\": \"" + escapeJson(addr.toString()) + "\",");
            writer.println("  \"status\": \"" + status + "\",");
            writer.println("  \"kind\": \"" + escapeJson(kind) + "\",");
            writer.println("  \"oldName\": \"" + escapeJson(oldName) + "\",");
            writer.println("  \"newName\": \"" + escapeJson(newName) + "\",");
            writer.println("  \"error\": \"" + escapeJson(error) + "\"");
            writer.println("}");
        }

        println("Rename result written to: " + outputFile.getAbsolutePath());
    }

    private String escapeJson(String s) {
        if (s == null) return "";
        StringBuilder sb = new StringBuilder(s.length() + 16);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '\\': sb.append("\\\\"); break;
                case '"':  sb.append("\\\""); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                case '\b': sb.append("\\b"); break;
                case '\f': sb.append("\\f"); break;
                default:
                    if (c < 0x20) {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
            }
        }
        return sb.toString();
    }
}
