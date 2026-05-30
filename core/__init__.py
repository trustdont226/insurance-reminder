"""
Insurance Reminder — core application modules.

Modules:
    config         – Centralised environment configuration
    database       – Persistence layer (SQLite today, Supabase Postgres next)
    pdf_processor  – PDF rendering + EasyOCR field extraction
    storage        – File storage helper (local today, Supabase Storage next)
    whatsapp       – Click-to-Chat URL builder + message template
    scheduler      – Background scheduler for daily due-list job
"""
