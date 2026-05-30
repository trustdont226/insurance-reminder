"""
core/config.py
Centralised configuration. All env vars are read here so other modules don't
need to call `os.getenv` directly.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env once, as early as possible
load_dotenv()


# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR      = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
DB_PATH       = os.getenv("DB_PATH",       str(BASE_DIR / "insurance_records.db"))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ── Server ────────────────────────────────────────────────────────────────────

PORT      = int(os.getenv("PORT", "5000"))
HOST      = os.getenv("HOST", "0.0.0.0")
DEBUG     = os.getenv("DEBUG", "false").lower() == "true"


# ── Timezone & scheduler ──────────────────────────────────────────────────────

TIMEZONE  = os.getenv("TIMEZONE", "Asia/Kolkata")


# ── Supabase (used once we migrate from SQLite) ───────────────────────────────

DATABASE_URL  = os.getenv("DATABASE_URL", "")
SUPABASE_URL  = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY  = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "pdfs")


def using_supabase() -> bool:
    """True when full Supabase credentials are present."""
    return bool(DATABASE_URL and SUPABASE_URL and SUPABASE_KEY)
