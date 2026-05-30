"""
core/storage.py
File storage helper — uploads PDFs to Supabase Storage.

Flow when a PDF is uploaded:
  1) save_pdf_temp()           – write to local /tmp for OCR
  2) <OCR runs on the temp file>
  3) upload_to_supabase()      – push the file to Supabase Storage
  4) delete_temp()             – remove the local copy

Render's free tier has an ephemeral disk, so all persistent storage MUST
live in Supabase.
"""

import os
import tempfile
import uuid
from functools import lru_cache
from pathlib import Path

from core.config import SUPABASE_BUCKET, SUPABASE_KEY, SUPABASE_URL, UPLOAD_FOLDER


# ── Supabase client (singleton) ───────────────────────────────────────────────

@lru_cache(maxsize=1)
def _client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_KEY are not set. Configure them in .env "
            "(local) or in Render → Environment (production)."
        )
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Temp local save (for OCR) ─────────────────────────────────────────────────

def save_pdf_temp(file_storage, filename: str) -> str:
    """
    Save the uploaded PDF to a local temp location so OCR can read it.
    Returns the local file path.
    """
    # Always use a tempdir — works on both local and Render
    temp_dir = tempfile.gettempdir()
    safe_name = f"{uuid.uuid4().hex}_{Path(filename).name}"
    temp_path = os.path.join(temp_dir, safe_name)
    file_storage.save(temp_path)
    return temp_path


# ── Supabase upload ───────────────────────────────────────────────────────────

def upload_to_supabase(local_path: str, original_filename: str) -> str:
    """
    Upload a local PDF to Supabase Storage and return the storage key
    (path inside the bucket). Filenames are prefixed with a UUID to avoid
    collisions when two customers have the same PDF name.
    """
    storage_key = f"{uuid.uuid4().hex}_{Path(original_filename).name}"

    with open(local_path, "rb") as f:
        file_bytes = f.read()

    client = _client()
    client.storage.from_(SUPABASE_BUCKET).upload(
        path=storage_key,
        file=file_bytes,
        file_options={"content-type": "application/pdf"},
    )
    return storage_key


def get_signed_url(storage_key: str, expires_in_seconds: int = 3600) -> str | None:
    """
    Create a short-lived signed URL so the agent can download a PDF if needed.
    Bucket is private, so direct URLs don't work.
    """
    try:
        client = _client()
        resp = client.storage.from_(SUPABASE_BUCKET).create_signed_url(
            storage_key, expires_in_seconds
        )
        return resp.get("signedURL") or resp.get("signedUrl")
    except Exception:
        return None


def delete_from_supabase(storage_key: str) -> bool:
    """Remove a PDF from Supabase Storage."""
    try:
        client = _client()
        client.storage.from_(SUPABASE_BUCKET).remove([storage_key])
        return True
    except Exception:
        return False


# ── Local temp cleanup ────────────────────────────────────────────────────────

def delete_temp(local_path: str) -> bool:
    """Remove a local temp file."""
    try:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
            return True
    except OSError:
        pass
    return False


# ── Convenience: save_pdf — kept for backwards compatibility ──────────────────

def save_pdf(file_storage, filename: str) -> str:
    """
    Legacy helper that just saves to UPLOAD_FOLDER (used only when Supabase
    creds are not configured, e.g. running locally without env vars).
    """
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file_storage.save(path)
    return path
