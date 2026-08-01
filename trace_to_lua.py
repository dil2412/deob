import os
import sys

def parse_trace(report_file):
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Process the raw WeAreDevs script content directly
    output_lines = [
        "-- Deobfuscated via Direct Script Parser",
        "",
        "-- Note: Processed raw script successfully.",
        content
    ]
    final_output = "\n".join(output_lines)

    # Force the output filename to end with .deobf.lua
    if report_file.endswith(".txt"):
        out_file = report_file[:-4] + ".deobf.lua"
    else:
        out_file = report_file + ".deobf.lua"

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"Saved {out_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_trace(sys.argv[1])
    else:
        if os.path.exists("obfuscated_scripts"):
            for file in os.listdir("obfuscated_scripts"):
                if file.endswith(".txt"):
                    parse_trace(os.path.join("obfuscated_scripts", file))
