# Architecture

## High-Level Diagram

```
┌──────────────┐   HTTPS    ┌────────────────────────────┐    SQL/REST   ┌──────────────┐
│              │ ─────────► │     Render (free)          │ ────────────► │   Supabase   │
│   Browser    │            │   ┌──────────────────────┐ │               │              │
│  (Chrome)    │            │   │ Flask app            │ │ ─── Storage ► │  Postgres DB │
│              │ ◄───────── │   │  • app.py            │ │               │  Storage     │
└──────────────┘            │   │  • core/             │ │               │              │
                            │   │  • templates/        │ │               └──────────────┘
                            │   └──────────────────────┘ │
                            └────────────────────────────┘
```

---

## Module Layout

```
insurance-reminder/
├── app.py            # Flask entry point + routes
└── core/             # Application logic
    ├── config.py     # Env var loader
    ├── database.py   # CRUD operations
    ├── pdf_processor.py
    ├── storage.py    # File save/delete
    ├── whatsapp.py   # wa.me URL builder
    └── scheduler.py  # Daily due-list job
```

---

## Request Flow — Upload PDF

```
1.  Browser uploads PDF                       → POST /api/upload
2.  app.py             save_pdf(file)         → core/storage.py
3.  core/storage.py    writes file            → Supabase Storage
4.  app.py             extract_insurance_data → core/pdf_processor.py
5.  core/pdf_processor → fitz → numpy → EasyOCR → regex → dict
6.  app.py             insert_record(dict)    → core/database.py
7.  core/database.py   INSERT INTO            → Supabase Postgres
8.  app.py             JSON response          → Browser
```

## Request Flow — Send Reminder

```
1.  Browser clicks WhatsApp button            → POST /api/send-reminder/<id>
2.  app.py             build_whatsapp_url     → core/whatsapp.py
3.  core/whatsapp      reads template         → core/database.py (get_setting)
4.  core/whatsapp      builds wa.me URL       → app.py
5.  app.py             marks reminder_sent    → core/database.py
6.  app.py             returns URL            → Browser
7.  Browser opens wa.me URL in new tab        → WhatsApp Web
8.  Agent clicks Send                         → Customer receives message
```

---

## Why This Layout

- **`core/` separation** — All business logic lives outside the Flask routes. Swapping the database (SQLite → Supabase) or storage (local → cloud) only touches one file.
- **`config.py`** — Single source of truth for env vars. No `os.getenv` scattered everywhere.
- **`scheduler.py` as a module** — Background scheduler is a singleton; the routes call `apply_settings()` whenever the time changes.

---

## Data Model

### `insurance_records`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| owner_name | TEXT | |
| mobile_number | TEXT | 10-digit Indian format |
| policy_number | TEXT | |
| vehicle_number | TEXT | |
| chassis_number | TEXT | |
| engine_number | TEXT | |
| renewal_date | TEXT | `DD/MM/YYYY` |
| payment_due_date | TEXT | `DD/MM/YYYY` |
| premium_amount | TEXT | |
| vehicle_make_model | TEXT | |
| issuing_office | TEXT | |
| reminder_sent | INTEGER | 0/1 |
| reminder_sent_at | TEXT | ISO timestamp |
| pdf_filename | TEXT | |
| created_at | TIMESTAMP | |

### `settings` (key/value)

| Key | Default |
|---|---|
| reminder_days | `3` |
| scheduler_enabled | `false` |
| scheduler_time | `09:00` |
| scheduler_last_run | `` |
| scheduler_last_result | `` |
| message_template | (default template) |
