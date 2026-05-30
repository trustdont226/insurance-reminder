# Insurance Renewal Reminder

A Flask web app for insurance agents to manage vehicle insurance renewal data and send WhatsApp reminders to customers.

## Features

- Upload PDF renewal notices — auto-extract owner name, mobile, vehicle/policy number, dates, premium
- Manage records — search, filter, edit, delete
- Send WhatsApp reminders via Click-to-Chat (no API/verification required)
- Bulk send with sequential modal (one customer at a time)
- Customizable message template with live preview
- Excel export of all records
- Daily scheduler to identify due reminders

## Requirements

- Python 3.10+
- ~500 MB free disk space (for EasyOCR models)
- Modern browser (Chrome/Edge)
- WhatsApp installed on phone or WhatsApp Web logged in

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py
```

First run downloads EasyOCR models (~50 MB, one-time).

Open `http://localhost:5000` in your browser.

## Network Access

The app binds to `0.0.0.0:5000` — accessible from any device on your local network:

```
http://<your-pc-ip>:5000
```

Find your PC's IP with `ipconfig` (Windows) or `ifconfig` (Mac/Linux).

## Usage

1. **Upload PDF** — drop one or more insurance renewal notice PDFs
2. **Review extracted data** — edit any field if OCR missed something
3. **Send Reminder** — click the WhatsApp button on a record
   - WhatsApp Web / mobile app opens with pre-filled message
   - Click Send to deliver
4. **Customize template** — go to Settings → WhatsApp Message Template
5. **Auto-scheduler** — set a daily time to scan for due reminders

## Files

| File | Purpose |
|---|---|
| `app.py` | Flask backend & routes |
| `database.py` | SQLite persistence |
| `pdf_processor.py` | PDF rendering + EasyOCR extraction |
| `whatsapp.py` | Click-to-Chat URL builder & message template |
| `templates/index.html` | Single-page UI |
| `requirements.txt` | Python dependencies |

## License

Private use.
