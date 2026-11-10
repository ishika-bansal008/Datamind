import asyncio
from io import BytesIO

from fastapi import UploadFile

from app.services.documents import extract_document


def _upload(name: str, payload: bytes) -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(payload))


def test_csv_extracts_every_row_as_pipe_table():
    result, filename = asyncio.run(extract_document(
        _upload("projects.csv", b"Project ID,Domain,Title\nP-01,Health,Wellness assistant\nP-02,Education,Learning helper\n"),
        1024 * 1024,
        10000,
    ))
    assert filename == "projects.csv"
    assert "P-01" in result and "P-02" in result
    assert "| Project ID | Domain | Title |" in result


def test_json_list_of_objects_becomes_complete_table():
    result, filename = asyncio.run(extract_document(
        _upload("items.json", b'[{"id":"A1","name":"Alpha"},{"id":"B2","name":"Beta"}]'),
        1024 * 1024,
        10000,
    ))
    assert filename == "items.json"
    assert "A1" in result and "B2" in result
    assert "| id | name |" in result
