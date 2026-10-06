/* ###
 * Add a comment (plate/pre/eol/post/repeatable) at an address.
 * @category Modify
 */

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CommentType;
import ghidra.program.model.listing.Listing;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

public class AddComment extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 3) {
            println("Usage: AddComment.java <address> <type> <text...>");
            println("  type: plate | pre | eol | post | repeatable");
            println("  Example: AddComment.java 0x00123456 eol check return value here");
            return;
        }

        String addrStr = args[0];
        String typeStr = args[1].toLowerCase();

        Address addr;
        try {
            addr = currentProgram.getAddressFactory().getAddress(addrStr);
        } catch (Exception e) {
            println("ERROR: invalid address '" + addrStr + "': " + e.getMessage());
            return;
        }

        CommentType commentType;
        switch (typeStr) {
            case "plate":      commentType = CommentType.PLATE;      break;
            case "pre":        commentType = CommentType.PRE;        break;
            case "eol":        commentType = CommentType.EOL;        break;
            case "post":       commentType = CommentType.POST;       break;
            case "repeatable": commentType = CommentType.REPEATABLE; break;
            default:
                println("ERROR: invalid comment type '" + args[1] + "'.");
                println("  Valid types: plate, pre, eol, post, repeatable");
                return;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 2; i < args.length; i++) {
            if (i > 2) sb.append(' ');
            sb.append(args[i]);
        }
        String text = sb.toString();

        Listing listing = currentProgram.getListing();
        listing.setComment(addr, commentType, text);

        // Read back to confirm the comment landed.
        String readBack = listing.getComment(commentType, addr);
        boolean verified = text.equals(readBack);

        String outputDir = System.getenv("GHIDRA_OUTPUT_DIR");
        if (outputDir == null || outputDir.isEmpty()) {
            outputDir = ".";
        }

        String programName = currentProgram.getName().replaceAll("[^a-zA-Z0-9._-]", "_");
        File outputFile = new File(outputDir, programName + "_comment.json");

        try (PrintWriter writer = new PrintWriter(new FileWriter(outputFile))) {
            writer.println("{");
            writer.println("  \"program\": \"" + escapeJson(currentProgram.getName()) + "\",");
            writer.println("  \"address\": \"" + escapeJson(addr.toString()) + "\",");
            writer.println("  \"type\": \"" + escapeJson(typeStr) + "\",");
            writer.println("  \"text\": \"" + escapeJson(text) + "\",");
            writer.println("  \"verified\": " + verified);
            writer.println("}");
        }

        println("Set " + typeStr + " comment at " + addr + ": " + text
                + (verified ? " [verified]" : " [WARNING: read-back mismatch]"));
        println("Comment result written to: " + outputFile.getAbsolutePath());
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
