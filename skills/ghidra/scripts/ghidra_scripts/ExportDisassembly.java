/* ###
 * Export disassembly for an address range or a whole function.
 * Usage: <start> <end>        -> disassemble [start, end]
 *        <functionAddress>    -> disassemble the function containing it
 * Output text lines:  address: bytes  mnemonic operands
 * @category Export
 */

import ghidra.app.script.GhidraScript;
import ghidra.program.database.code.InstructionDB;
import ghidra.program.database.function.FunctionDB;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.CodeUnitIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

public class ExportDisassembly extends GhidraScript {

    private static final int MAX_UNITS = 20000;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("Usage: ExportDisassembly.java <start> <end> | <functionAddress>");
            println("  Example: ExportDisassembly.java 0x00101000 0x00101100");
            println("  Example: ExportDisassembly.java 0x00101000   (whole containing function)");
            return;
        }

        AddressSetView set;
        String scopeDesc;

        try {
            if (args.length >= 2) {
                Address start = currentProgram.getAddressFactory().getAddress(args[0]);
                Address end = currentProgram.getAddressFactory().getAddress(args[1]);
                if (start == null || end == null) {
                    println("ERROR: invalid address '"
                            + (start == null ? args[0] : args[1]) + "'");
                    return;
                }
                if (start.compareTo(end) > 0) {
                    println("ERROR: start address " + start + " is after end address " + end);
                    return;
                }
                set = new AddressSet(start, end);
                scopeDesc = start + " - " + end;
            } else {
                Address addr = currentProgram.getAddressFactory().getAddress(args[0]);
                if (addr == null) {
                    println("ERROR: invalid address '" + args[0] + "'");
                    return;
                }
                Function func = currentProgram.getFunctionManager().getFunctionContaining(addr);
                if (func == null) {
                    println("ERROR: no function contains address " + addr);
                    return;
                }
                if (!(func instanceof FunctionDB)) {
                    println("ERROR: cannot read body of function " + func.getName());
                    return;
                }
                set = ((FunctionDB) func).getBody();
                scopeDesc = "function " + func.getName() + " at " + func.getEntryPoint();
            }
        } catch (Exception e) {
            println("ERROR: invalid address argument: " + e.getMessage());
            return;
        }

        String outputDir = System.getenv("GHIDRA_OUTPUT_DIR");
        if (outputDir == null || outputDir.isEmpty()) {
            outputDir = ".";
        }

        String programName = currentProgram.getName().replaceAll("[^a-zA-Z0-9._-]", "_");
        File outputFile = new File(outputDir, programName + "_disassembly.txt");

        Listing listing = currentProgram.getListing();
        CodeUnitIterator units = listing.getCodeUnits(set, true);

        int count = 0;
        boolean truncated = false;

        try (PrintWriter writer = new PrintWriter(new FileWriter(outputFile))) {
            writer.println("; program: " + currentProgram.getName());
            writer.println("; scope: " + scopeDesc);

            while (units.hasNext() && !monitor.isCancelled()) {
                if (count >= MAX_UNITS) {
                    truncated = true;
                    break;
                }
                CodeUnit cu = units.next();
                writer.println(formatUnit(cu));
                count++;
            }

            if (truncated) {
                writer.println("; TRUNCATED at " + MAX_UNITS + " code units");
            }
        }

        println("Exported " + count + " code units (" + scopeDesc + ")"
                + (truncated ? " [TRUNCATED]" : ""));
        println("Disassembly written to: " + outputFile.getAbsolutePath());
    }

    private String formatUnit(CodeUnit cu) {
        String addrStr = cu.getMinAddress().toString();
        String bytesHex = formatBytes(cu);

        if (cu instanceof Instruction) {
            Instruction inst = (Instruction) cu;
            String mnemonic = getMnemonic(inst);
            StringBuilder ops = new StringBuilder();
            int numOps = inst.getPrototype().getNumOperands();
            for (int i = 0; i < numOps; i++) {
                if (i > 0) {
                    ops.append(inst.getSeparator(i));
                }
                ops.append(inst.getDefaultOperandRepresentation(i));
            }
            String tail = ops.length() > 0 ? " " + ops.toString() : "";
            return addrStr + ": " + bytesHex + "  " + mnemonic + tail;
        }
        return addrStr + ": " + bytesHex + "  ; data (" + cu.getLength() + " bytes)";
    }

    private String formatBytes(CodeUnit cu) {
        byte[] bytes;
        try {
            bytes = cu.getBytes();
        } catch (Exception e) {
            return "??";
        }
        if (bytes == null || bytes.length == 0) {
            return "--";
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < bytes.length; i++) {
            if (i > 0) sb.append(' ');
            sb.append(String.format("%02x", bytes[i] & 0xFF));
        }
        return sb.toString();
    }

    private String getMnemonic(Instruction inst) {
        try {
            // getMnemonicString() lives on the InstructionDB implementation
            // (not on the Instruction interface in this Ghidra version).
            return ((InstructionDB) inst).getMnemonicString();
        } catch (Exception e) {
            return inst.toString();
        }
    }
}

