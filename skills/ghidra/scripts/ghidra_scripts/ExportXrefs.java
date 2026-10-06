/* ###
 * List all references TO an address (code + data xrefs), FROM an address,
 * or both. Goes beyond the call graph: includes data reads/writes and
 * any other reference types Ghidra recorded.
 * @category Export
 */

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ExportXrefs extends GhidraScript {

    private static final int MAX_REFS = 10000;

    private static class Xref {
        String from;
        String to;
        String fromFunction; // may be null
        String refType;
        boolean isMemoryReference;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("Usage: ExportXrefs.java <address> [to|from|both]");
            println("  Example: ExportXrefs.java 0x00123456 both");
            return;
        }

        String addrStr = args[0];
        String direction = args.length >= 2 ? args[1].toLowerCase() : "both";
        if (!direction.equals("to") && !direction.equals("from") && !direction.equals("both")) {
            println("ERROR: direction must be one of: to | from | both (got '" + args[1] + "')");
            return;
        }

        Address addr;
        try {
            addr = currentProgram.getAddressFactory().getAddress(addrStr);
        } catch (Exception e) {
            addr = null;
        }
        if (addr == null) {
            println("ERROR: invalid address '" + addrStr + "'");
            return;
        }

        ReferenceManager refMgr = currentProgram.getReferenceManager();
        FunctionManager funcMgr = currentProgram.getFunctionManager();

        List<Xref> refs = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        boolean truncated = false;

        if (direction.equals("to") || direction.equals("both")) {
            ReferenceIterator it = refMgr.getReferencesTo(addr);
            while (it.hasNext() && !monitor.isCancelled()) {
                if (!addRef(refs, seen, it.next(), funcMgr)) {
                    truncated = true;
                    break;
                }
            }
        }
        if (!truncated && (direction.equals("from") || direction.equals("both"))) {
            Reference[] fromRefs = refMgr.getReferencesFrom(addr);
            for (Reference ref : fromRefs) {
                if (monitor.isCancelled()) break;
                if (!addRef(refs, seen, ref, funcMgr)) {
                    truncated = true;
                    break;
                }
            }
        }

        String outputDir = System.getenv("GHIDRA_OUTPUT_DIR");
        if (outputDir == null || outputDir.isEmpty()) {
            outputDir = ".";
        }

        String programName = currentProgram.getName().replaceAll("[^a-zA-Z0-9._-]", "_");
        File outputFile = new File(outputDir, programName + "_xrefs.json");

        try (PrintWriter writer = new PrintWriter(new FileWriter(outputFile))) {
            writer.println("{");
            writer.println("  \"program\": \"" + escapeJson(currentProgram.getName()) + "\",");
            writer.println("  \"target\": \"" + escapeJson(addr.toString()) + "\",");
            writer.println("  \"direction\": \"" + direction + "\",");
            writer.println("  \"references\": [");

            for (int i = 0; i < refs.size(); i++) {
                Xref x = refs.get(i);
                if (i > 0) writer.println(",");
                writer.println("    {");
                writer.println("      \"from\": \"" + escapeJson(x.from) + "\",");
                writer.println("      \"to\": \"" + escapeJson(x.to) + "\",");
                writer.println("      \"fromFunction\": "
                        + (x.fromFunction == null ? "null" : "\"" + escapeJson(x.fromFunction) + "\"") + ",");
                writer.println("      \"refType\": \"" + escapeJson(x.refType) + "\",");
                writer.println("      \"isMemoryReference\": " + x.isMemoryReference);
                writer.print("    }");
            }

            writer.println();
            writer.println("  ],");
            writer.println("  \"count\": " + refs.size() + ",");
            writer.println("  \"truncated\": " + truncated);
            writer.println("}");
        }

        println("Exported " + refs.size() + " xrefs (" + direction + ") for "
                + addr + (truncated ? " [TRUNCATED at " + MAX_REFS + "]" : ""));
        println("Xrefs written to: " + outputFile.getAbsolutePath());
    }

    /** Adds a reference unless already seen; returns false when the cap is hit. */
    private boolean addRef(List<Xref> refs, Set<String> seen, Reference ref, FunctionManager funcMgr) {
        if (refs.size() >= MAX_REFS) {
            return false;
        }
        String from = ref.getFromAddress().toString();
        String to = ref.getToAddress().toString();
        String refType = ref.getReferenceType().getName();
        String key = from + "->" + to + ":" + refType;
        if (!seen.add(key)) {
            return true; // duplicate (e.g. self-ref seen in both directions)
        }
        Xref x = new Xref();
        x.from = from;
        x.to = to;
        x.refType = refType;
        x.isMemoryReference = ref.isMemoryReference();
        Function f = funcMgr.getFunctionContaining(ref.getFromAddress());
        x.fromFunction = (f != null) ? f.getName() : null;
        refs.add(x);
        return true;
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
