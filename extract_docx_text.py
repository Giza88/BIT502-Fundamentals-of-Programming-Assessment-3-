"""
One-off script: extract text from a .docx file into a readable .txt file.
Uses only Python standard library (zipfile + xml).
Run from the Assessment_3 folder: python extract_docx_text.py
"""
import zipfile
import xml.etree.ElementTree as ET
import os
import tempfile

# Namespace used in Word document XML
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

def get_text_from_docx(docx_path):
    """Extract all paragraph text from a .docx file."""
    text_parts = []
    with zipfile.ZipFile(docx_path, "r") as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            for elem in root.iter():
                if elem.tag.endswith("}p"):  # paragraph
                    para_text = []
                    for t in elem.iter():
                        if t.tag.endswith("}t") and t.text:
                            para_text.append(t.text)
                        if t.tag.endswith("}t") and t.tail:
                            para_text.append(t.tail)
                    line = "".join(para_text).strip()
                    if line:
                        text_parts.append(line)
    return "\n".join(text_parts)

def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    # Set which docx to extract: "A" or "B"
    which = "A"
    if which == "A":
        docx_name = "Appendix_A___The_Aurora_Archive_Membership_Form.docx"
        title = "Appendix A – The Aurora Archive Membership Form"
    else:
        docx_name = "BIT502_Assessment_3_Appendix_B.docx"
        title = "Appendix B – Database Information"
    docx_path = os.path.join(folder, docx_name)
    if not os.path.isfile(docx_path):
        print(f"File not found: {docx_path}")
        print("Put the Appendix A .docx in the same folder as this script and run again.")
        return

    text = get_text_from_docx(docx_path)
    out_path = os.path.join(tempfile.gettempdir(), f"Appendix_{which}_READABLE.txt")
    try:
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(title + "\n")
            f.write("=" * 50 + "\n\n")
            f.write(text)
        print(f"Done. Readable text saved to:\n  {out_path}")
    except OSError as e:
        print("Could not write file:", e)
        print("\n--- Extracted text (copy to a .txt file if needed) ---\n")
        print(title)
        print("=" * 50)
        print(text)

if __name__ == "__main__":
    main()
