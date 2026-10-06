/* ###
 * Search raw memory (loaded + initialized blocks) for a Java regex.
 * Scans bytes directly, so it also finds matches that Ghidra has NOT
 * defined as strings. Bytes are decoded 1:1 to chars (Latin-1) before
 * the regex is applied.
 * @category Search
 */

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.MemoryBlock;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

public class SearchStrings extends GhidraScript {

    private static final int MAX_MATCHES = 5000;
    private static final int MAX_DISPLAY_LEN = 200;
    private static final int CHUNK_SIZE = 8 * 1024 * 1024;
    private static final int CHUNK_OVERLAP = 256; // catch matches crossing chunk borders

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("Usage: SearchStrings.java <regex> [minLen]");
            println("  Example: SearchStrings.java \"Error.*failed\" 6");
            println("  Scans loaded+initialized memory blocks; caps at "
                    + MAX_MATCHES + " matches.");
            return;
        }

        Pattern pattern;
        try {
            pattern = Pattern.compile(args[0]);
        } catch (PatternSyntaxException e) {
            println("ERROR: invalid regex '" + args[0] + "': " + e.getMessage());
            return;
        }

        int minLen = 4;
        if (args.length >= 2) {
            try {
                minLen = Integer.parseInt(args[1]);
            } catch (NumberFormatException e) {
                println("ERROR: minLen must be an integer (got '" + args[1] + "')");
                return;
            }
            if (minLen < 1) {
                println("ERROR: minLen must be >= 1");
                return;
            }
        }

        String outputDir = System.getenv("GHIDRA_OUTPUT_DIR");
        if (outputDir == null || outputDir.isEmpty()) {
            outputDir = ".";
        }

        String programName = currentProgram.getName().replaceAll("[^a-zA-Z0-9._-]", "_");
        File outputFile = new File(outputDir, programName + "_searchstrings.json");

        int totalMatches = 0;
        int blocksScanned = 0;
        boolean truncated = false;

        try (PrintWriter writer = new PrintWriter(new FileWriter(outputFile))) {
            writer.println("{");
            writer.println("  \"program\": \"" + escapeJson(currentProgram.getName()) + "\",");
            writer.println("  \"regex\": \"" + escapeJson(args[0]) + "\",");
            writer.println("  \"minLen\": " + minLen + ",");
            writer.println("  \"matches\": [");

            boolean first = true;

            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                if (monitor.isCancelled()) break;
                if (totalMatches >= MAX_MATCHES) {
                    truncated = true;
                    break;
                }
                if (!block.isLoaded() || !block.isInitialized()) {
                    continue;
                }
                blocksScanned++;

                long blockSize = block.getSize();
                Address blockStart = block.getStart();

                for (long off = 0; off < blockSize; off += CHUNK_SIZE) {
                    if (monitor.isCancelled() || totalMatches >= MAX_MATCHES) break;

                    int mainLen = (int) Math.min(CHUNK_SIZE, blockSize - off);
                    int extra = (int) Math.min(CHUNK_OVERLAP, blockSize - off - mainLen);
                    byte[] buf = new byte[mainLen + extra];

                    int bytesRead;
                    try {
                        bytesRead = block.getBytes(blockStart.add(off), buf);
                    } catch (Exception e) {
                        break; // unreadable region: skip rest of this block
                    }
                    if (bytesRead <= 0) break;

                    // 1 byte -> 1 char (Latin-1), so offsets stay exact.
                    char[] chars = new char[bytesRead];
                    for (int i = 0; i < bytesRead; i++) {
                        chars[i] = (char) (buf[i] & 0xFF);
                    }
                    Matcher m = pattern.matcher(new String(chars));

                    while (m.find()) {
                        int start = m.start();
                        if (start >= mainLen) {
                            continue; // belongs to the next chunk
                        }
                        String match = m.group();
                        if (match.length() < minLen) {
                            continue;
                        }
                        if (totalMatches >= MAX_MATCHES) {
                            truncated = true;
                            break;
                        }

                        String display = match.length() > MAX_DISPLAY_LEN
                                ? match.substring(0, MAX_DISPLAY_LEN) : match;
                        boolean displayCut = match.length() > MAX_DISPLAY_LEN;
                        String matchAddr;
                        try {
                            matchAddr = blockStart.add(off + start).toString();
                        } catch (Exception e) {
                            matchAddr = block.getName() + "+0x" + Long.toHexString(off + start);
                        }

                        if (!first) writer.println(",");
                        first = false;
                        writer.println("    {");
                        writer.println("      \"address\": \"" + escapeJson(matchAddr) + "\",");
                        writer.println("      \"block\": \"" + escapeJson(block.getName()) + "\",");
                        writer.println("      \"length\": " + match.length() + ",");
                        writer.println("      \"displayTruncated\": " + displayCut + ",");
                        writer.println("      \"string\": \"" + escapeJson(display) + "\"");
                        writer.print("    }");
                        totalMatches++;
                    }
                }
            }

            writer.println();
            writer.println("  ],");
            writer.println("  \"count\": " + totalMatches + ",");
            writer.println("  \"blocksScanned\": " + blocksScanned + ",");
            writer.println("  \"truncated\": " + truncated);
            writer.println("}");
        }

        println("Searched " + blocksScanned + " memory blocks, found " + totalMatches
                + " matches for /" + args[0] + "/ (minLen " + minLen + ")"
                + (truncated ? " [TRUNCATED at " + MAX_MATCHES + "]" : ""));
        println("Matches written to: " + outputFile.getAbsolutePath());
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

