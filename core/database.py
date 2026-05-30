"""
core/database.py
PostgreSQL persistence layer (Supabase Postgres).

All public function signatures match the old SQLite version, so other
modules don't need any changes when the backend swaps.
"""

import psycopg2
import psycopg2.extras

from core.config import DATABASE_URL


# ── Connection ────────────────────────────────────────────────────────────────

def get_connection():
    """Return a new Postgres connection with dict-row factory."""
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Configure it in .env (local) or in "
            "Render → Environment (production)."
        )
    return psycopg2.connect(DATABASE_URL)


def _dict_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# ── Settings (key/value store) ────────────────────────────────────────────────

def get_setting(key: str, default=None):
    conn = get_connection()
    try:
        with _dict_cursor(conn) as cur:
            cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
            row = cur.fetchone()
            return row["value"] if row else default
    finally:
        conn.close()


def set_setting(key: str, value):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO settings (key, value) VALUES (%s, %s) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                (key, str(value)),
            )
        conn.commit()
    finally:
        conn.close()


# ── Schema bootstrap ──────────────────────────────────────────────────────────

def init_db():
    """Create tables and seed default settings (idempotent)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS insurance_records (
                    id                 SERIAL PRIMARY KEY,
                    owner_name         TEXT,
                    mobile_number      TEXT,
                    policy_number      TEXT,
                    vehicle_number     TEXT,
                    chassis_number     TEXT,
                    engine_number      TEXT,
                    renewal_date       TEXT,
                    payment_due_date   TEXT,
                    premium_amount     TEXT,
                    vehicle_make_model TEXT,
                    issuing_office     TEXT,
                    reminder_sent      INTEGER DEFAULT 0,
                    reminder_sent_at   TEXT,
                    pdf_filename       TEXT,
                    pdf_storage_path   TEXT,
                    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Make sure the new pdf_storage_path column exists if table is older
            cur.execute("""
                ALTER TABLE insurance_records
                ADD COLUMN IF NOT EXISTS pdf_storage_path TEXT
            """)

            # Seed default settings
            defaults = {
                "reminder_days":         "3",
                "scheduler_enabled":     "false",
                "scheduler_time":        "09:00",
                "scheduler_last_run":    "",
                "scheduler_last_result": "",
                "message_template": (
                    "Dear {owner},\n\n"
                    "This is a friendly reminder that your vehicle insurance is due for renewal.\n\n"
                    "*Vehicle Number:* {vehicle}\n"
                    "*Policy Number:* {policy}\n"
                    "*Renewal Date:* {renewal}\n"
                    "*Premium Amount:* Rs. {premium}\n"
                    "*Status:* {days}\n\n"
                    "Please renew before the due date to avoid policy lapse.\n\n"
                    "For any queries, feel free to contact us.\n\n"
                    "Thank you,\n"
                    "Rahane Insurance Agency"
                ),
            }
            for key, value in defaults.items():
                cur.execute(
                    "INSERT INTO settings (key, value) VALUES (%s, %s) "
                    "ON CONFLICT (key) DO NOTHING",
                    (key, value),
                )
        conn.commit()
    finally:
        conn.close()


# ── CRUD: insurance_records ───────────────────────────────────────────────────

def insert_record(data: dict) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO insurance_records
                    (owner_name, mobile_number, policy_number, vehicle_number,
                     chassis_number, engine_number, renewal_date, payment_due_date,
                     premium_amount, vehicle_make_model, issuing_office,
                     pdf_filename, pdf_storage_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    data.get("owner_name"),
                    data.get("mobile_number"),
                    data.get("policy_number"),
                    data.get("vehicle_number"),
                    data.get("chassis_number"),
                    data.get("engine_number"),
                    data.get("renewal_date"),
                    data.get("payment_due_date"),
                    data.get("premium_amount"),
                    data.get("vehicle_make_model"),
                    data.get("issuing_office"),
                    data.get("pdf_filename"),
                    data.get("pdf_storage_path"),
                ),
            )
            record_id = cur.fetchone()[0]
        conn.commit()
        return record_id
    finally:
        conn.close()


def get_all_records() -> list:
    conn = get_connection()
    try:
        with _dict_cursor(conn) as cur:
            cur.execute(
                "SELECT * FROM insurance_records ORDER BY renewal_date ASC NULLS LAST"
            )
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_record_by_id(record_id: int) -> dict | None:
    conn = get_connection()
    try:
        with _dict_cursor(conn) as cur:
            cur.execute("SELECT * FROM insurance_records WHERE id = %s", (record_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def update_record(record_id: int, data: dict):
    allowed = {
        "owner_name", "mobile_number", "policy_number", "vehicle_number",
        "chassis_number", "engine_number", "renewal_date", "payment_due_date",
        "premium_amount", "vehicle_make_model", "issuing_office",
        "reminder_sent", "reminder_sent_at", "pdf_storage_path",
    }
    fields, values = [], []
    for field in allowed:
        if field in data:
            fields.append(f"{field} = %s")
            values.append(data[field])

    if not fields:
        return

    values.append(record_id)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE insurance_records SET {', '.join(fields)} WHERE id = %s",
                values,
            )
        conn.commit()
    finally:
        conn.close()


def delete_record(record_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM insurance_records WHERE id = %s", (record_id,))
        conn.commit()
    finally:
        conn.close()
