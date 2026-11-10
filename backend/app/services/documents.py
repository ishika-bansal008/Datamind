import csv
import json
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader


def _safe_pipe(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def _records_to_markdown_table(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    headers: list[str] = []
    for record in records:
        for key in record:
            label = str(key)
            if label not in headers:
                headers.append(label)
    if not headers:
        return ""
    lines = ["| " + " | ".join(_safe_pipe(item) for item in headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for record in records:
        lines.append("| " + " | ".join(_safe_pipe(record.get(key, "")) for key in headers) + " |")
    return "\n".join(lines)


def _json_to_text(raw_text: str) -> str:
    try:
        value = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON file: {exc.msg} (line {exc.lineno}, column {exc.colno}).") from exc

    # Convert the largest list-of-objects into a table so source rows can be preserved.
    record_lists: list[list[dict[str, Any]]] = []
    def visit(node: Any) -> None:
        if isinstance(node, list):
            if node and all(isinstance(item, dict) for item in node):
                record_lists.append(node)
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            for item in node.values():
                visit(item)
    visit(value)
    if record_lists:
        records = max(record_lists, key=len)
        table = _records_to_markdown_table(records)
        if table:
            return table + "\n\nStructured JSON source contains " + str(len(records)) + " records."
    return json.dumps(value, ensure_ascii=False, indent=2)


def _csv_to_text(raw_text: str) -> str:
    sample = raw_text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(StringIO(raw_text), dialect))
    rows = [[cell.strip() for cell in row] for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        raise ValueError("The CSV file contains no records.")
    if len(rows) == 1:
        return rows[0][0] if rows[0] else ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    return "\n".join("| " + " | ".join(_safe_pipe(cell) for cell in row) + " |" for row in rows)


async def extract_document(file: UploadFile, max_bytes: int, max_chars: int) -> tuple[str, str]:
    filename = Path(file.filename or "upload").name
    suffix = Path(filename).suffix.lower()
    allowed = {".txt", ".md", ".markdown", ".pdf", ".docx", ".csv", ".json"}
    if suffix not in allowed:
        raise ValueError("Unsupported file type. Upload PDF, DOCX, TXT, MD, CSV or JSON.")

    raw = await file.read(max_bytes + 1)
    if not raw:
        raise ValueError("The uploaded file is empty.")
    if len(raw) > max_bytes:
        raise ValueError(f"File is too large. Maximum upload size is {max_bytes // (1024 * 1024)} MB.")

    try:
        if suffix in {".txt", ".md", ".markdown"}:
            text = raw.decode("utf-8-sig", errors="replace")
        elif suffix == ".csv":
            text = _csv_to_text(raw.decode("utf-8-sig", errors="replace"))
        elif suffix == ".json":
            text = _json_to_text(raw.decode("utf-8-sig", errors="strict"))
        elif suffix == ".pdf":
            reader = PdfReader(BytesIO(raw))
            if reader.is_encrypted:
                raise ValueError("Password-protected PDFs are not supported.")
            chunks = []
            for page in reader.pages:
                try:
                    extracted = page.extract_text(extraction_mode="layout") or ""
                except TypeError:
                    extracted = page.extract_text() or ""
                chunks.append(extracted)
            text = "\n\n".join(chunks)
        else:
            doc = Document(BytesIO(raw))
            blocks = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    blocks.append(" | ".join(cell.text for cell in row.cells))
            text = "\n\n".join(blocks)
    except ValueError:
        raise
    except UnicodeDecodeError as exc:
        raise ValueError("This file encoding is not supported. Save it as UTF-8 and upload again.") from exc
    except Exception as exc:
        raise ValueError("Could not read this document. Check that it is a valid PDF/DOCX/TXT/MD/CSV/JSON file.") from exc

    text = text.strip()
    if not text:
        raise ValueError("No readable text was found in this document. Scanned PDFs need OCR, which is not enabled.")
    if len(text) > max_chars:
        text = text[:max_chars]
    return text, filename
