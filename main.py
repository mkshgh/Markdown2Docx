import re
import shutil
import subprocess
import sys
from pathlib import Path

# ==========================================
# CONFIG
# ==========================================

INPUT_MD = "nsp.md"
TEMP_MD = "processed.md"

OUTPUT_PDF = "blueprint.pdf"
OUTPUT_DOCX = "blueprint.docx"

# ==========================================
# STEP 1 — CHECK DEPENDENCIES
# ==========================================

commands = ["mmdc", "pandoc", "wkhtmltopdf"]

print("\n=== CHECKING DEPENDENCIES ===\n")

for cmd in commands:
    path = shutil.which(cmd)

    if path:
        print(f"[OK] {cmd} -> {path}")
    else:
        print(f"[ERROR] {cmd} NOT FOUND")
        sys.exit()

print("\n=================================\n")

# ==========================================
# STEP 2 — READ MARKDOWN
# ==========================================

print("[STEP] Reading markdown...")

content = Path(INPUT_MD).read_text(encoding="utf-8")
print("[OK] Markdown loaded\n")

# ==========================================
# STEP 3 — FIND MERMAID BLOCKS
# ==========================================

print("[STEP] Searching Mermaid diagrams...")

pattern = r"```mermaid(.*?)```"
matches = re.findall(pattern, content, re.DOTALL)

print(f"[OK] Found {len(matches)} Mermaid chart(s)\n")

# ==========================================
# STEP 4 — RENDER MERMAID (HIGH QUALITY PNG)
# ==========================================

for i, chart in enumerate(matches):

    print(f"[STEP] Rendering chart {i}...")

    chart = chart.strip()

    mmd_file = f"chart_{i}.mmd"
    png_file = f"chart_{i}.png"

    Path(mmd_file).write_text(chart, encoding="utf-8")

    try:
        cmd = f'mmdc -i "{mmd_file}" -o "{png_file}" --scale 3 -b transparent'
        result = subprocess.run(cmd, shell=True)

        if result.returncode != 0:
            print(f"[FAILED] Mermaid rendering failed at chart {i}")
            sys.exit()

        print(f"[OK] Rendered: {png_file}")

    except Exception as e:
        print("[FAILED] Mermaid error:", e)
        sys.exit()

    # SAFE replacement (prevents mismatch issues)
    content = content.replace(
        f"```mermaid{matches[i]}```",
        f"![diagram]({png_file})"
    )

print()

# ==========================================
# STEP 5 — SAVE TEMP MARKDOWN
# ==========================================

print("[STEP] Saving processed markdown...")

Path(TEMP_MD).write_text(content, encoding="utf-8")
print(f"[OK] Saved: {TEMP_MD}\n")

# ==========================================
# STEP 6 — EXPORT PDF (STABLE WKHTMLTOPDF)
# ==========================================

print("[STEP] Exporting PDF...")

pdf_cmd = [
    "pandoc",
    TEMP_MD,
    "-o",
    OUTPUT_PDF,
    "--pdf-engine=wkhtmltopdf",

    # SAFE + STABLE OPTIONS ONLY
    "--pdf-engine-opt=--enable-local-file-access",
    "--pdf-engine-opt=--zoom",
    "--pdf-engine-opt=1.25",
    "--pdf-engine-opt=--dpi",
    "--pdf-engine-opt=300",
    "--pdf-engine-opt=--page-size",
    "--pdf-engine-opt=A4"
]

result = subprocess.run(pdf_cmd)

if result.returncode != 0:
    print("[FAILED] PDF generation failed")
    sys.exit()

print(f"[OK] PDF created: {OUTPUT_PDF}\n")

# ==========================================
# STEP 7 — EXPORT DOCX
# ==========================================

print("[STEP] Exporting DOCX...")

docx_cmd = [
    "pandoc",
    TEMP_MD,
    "-o",
    OUTPUT_DOCX
]

result = subprocess.run(docx_cmd)

if result.returncode != 0:
    print("[FAILED] DOCX generation failed")
    sys.exit()

print(f"[OK] DOCX created: {OUTPUT_DOCX}\n")

# ==========================================
# DONE
# ==========================================

print("=================================")
print("DONE — EXPORT COMPLETE")
print("=================================")