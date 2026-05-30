"""
core/storage.py
File storage helper.

Today it stores uploaded PDFs on the local filesystem (under uploads/).
When we migrate to Supabase, only this module needs to change — the upload
endpoint will call save_pdf()/delete_pdf() exactly the same way.
"""

import os
from pathlib import Path

from core.config import UPLOAD_FOLDER


def save_pdf(file_storage, filename: str) -> str:
    """
    Persist an uploaded PDF and return its identifier (path or storage key).
    `file_storage` is the Werkzeug FileStorage object from `request.files`.
    """
    path = os.path.join(UPLOAD_FOLDER, filename)
    file_storage.save(path)
    return path


def delete_pdf(identifier: str) -> bool:
    """Delete a PDF given the identifier returned by save_pdf()."""
    try:
        if os.path.exists(identifier):
            os.remove(identifier)
            return True
    except OSError:
        pass
    return False


def list_pdfs() -> list:
    """Return a list of filenames currently in storage."""
    folder = Path(UPLOAD_FOLDER)
    if not folder.exists():
        return []
    return [p.name for p in folder.iterdir() if p.suffix.lower() == ".pdf"]
