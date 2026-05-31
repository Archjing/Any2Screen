#!/usr/bin/env python3
"""
doc2md — Convert common document formats to Markdown.
Supports: .docx (incl. password-protected), .pdf, .txt

Usage:
  python3 doc2md.py <input> [--output <dir>] [--password <pw>]

Examples:
  python3 doc2md.py report.docx
  python3 doc2md.py article.pdf -o ~/output/
  python3 doc2md.py encrypted.docx --password mypass
  python3 doc2md.py /path/to/batch/ -o ~/output/ -p batchpass
"""
import os, sys, io, argparse
from docx import Document
import PyPDF2

try:
    import msoffcrypto
    HAS_MSOFFCRYPTO = True
except ImportError:
    HAS_MSOFFCRYPTO = False

def safe_filename(name):
    base = os.path.splitext(name)[0]
    return base + ".md"

def convert_docx(filepath, outpath, password=None):
    """Convert .docx to .md, decrypting if password-protected."""
    decrypted = None
    try:
        if HAS_MSOFFCRYPTO and password:
            with open(filepath, 'rb') as f:
                of = msoffcrypto.OfficeFile(f)
                if of.is_encrypted():
                    of.load_key(password=password)
                    buf = io.BytesIO()
                    of.decrypt(buf)
                    buf.seek(0)
                    decrypted = buf
        if decrypted is None:
            decrypted = filepath

        doc = Document(decrypted)
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                lines.append("")
                continue
            style = para.style.name if para.style else ""
            if "Heading 1" in style or "标题 1" in style:
                lines.append(f"# {text}")
            elif "Heading 2" in style or "标题 2" in style:
                lines.append(f"## {text}")
            elif "Heading 3" in style or "标题 3" in style:
                lines.append(f"### {text}")
            elif "Heading" in style or "标题" in style:
                lines.append(f"**{text}**")
            else:
                lines.append(text)

        with open(outpath, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(lines))
        return True, len(lines)
    except Exception as e:
        return False, str(e)

def convert_pdf(filepath, outpath):
    """Extract text from PDF as markdown."""
    try:
        reader = PyPDF2.PdfReader(filepath)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(pages))
        return True, len(pages)
    except Exception as e:
        return False, str(e)

def convert_txt(filepath, outpath):
    """Copy .txt as .md (passthrough)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as src:
            text = src.read()
        with open(outpath, 'w', encoding='utf-8') as dst:
            dst.write(text)
        return True, len(text.split('\n'))
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description="Convert documents to Markdown")
    parser.add_argument("input", help="File or directory to convert")
    parser.add_argument("-o", "--output", default=".", help="Output directory (default: current)")
    parser.add_argument("-p", "--password", default=None, help="Password for encrypted .docx files")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if os.path.isdir(args.input):
        files = [f for f in sorted(os.listdir(args.input))
                 if f.lower().endswith(('.docx', '.pdf', '.txt'))]
    else:
        files = [os.path.basename(args.input)]
        args.input = os.path.dirname(args.input) or '.'

    print(f"Converting {len(files)} file(s) → {args.output}")
    success, failed = 0, 0

    for fname in files:
        src = os.path.join(args.input, fname)
        dst = os.path.join(args.output, safe_filename(fname))
        ext = os.path.splitext(fname)[1].lower()

        print(f"  [{ext}] {fname[:55]}...", end=" ", flush=True)

        if ext == '.docx':
            ok, info = convert_docx(src, dst, args.password)
        elif ext == '.pdf':
            ok, info = convert_pdf(src, dst)
        elif ext == '.txt':
            ok, info = convert_txt(src, dst)
        else:
            ok, info = False, "unsupported format"

        if ok:
            print(f"✅ {info} lines")
            success += 1
        else:
            print(f"❌ {info}")
            failed += 1

    print(f"\nDone: {success} ok, {failed} failed")

if __name__ == "__main__":
    main()
