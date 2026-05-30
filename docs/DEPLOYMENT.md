# Deployment Guide

Step-by-step instructions for deploying the Insurance Reminder app to **Render (free)** with **Supabase** as the database.

---

## Prerequisites

- A GitHub account (the code lives in a Git repo)
- A free Supabase account ([supabase.com](https://supabase.com))
- A free Render account ([render.com](https://render.com))

---

## Part 1 — Supabase Setup

### 1. Create a Project

1. Sign up at [supabase.com](https://supabase.com)
2. **New Project** →
   - Name: `insurance-reminder`
   - Database Password: generate a strong one (save it!)
   - Region: closest to your users (e.g. `Mumbai`)
   - Plan: Free
3. Wait 2–3 minutes for provisioning

### 2. Create a Storage Bucket

1. Left sidebar → **Storage**
2. **New bucket** →
   - Name: `pdfs`
   - Public bucket: **OFF** (keep private)

### 3. Collect Credentials

You need three values:

| Variable | Where to find it |
|---|---|
| `DATABASE_URL` | Settings → Database → Connection string (URI mode) |
| `SUPABASE_URL` | Settings → API → Project URL |
| `SUPABASE_KEY` | Settings → API → anon / public key |

Save these — you'll paste them into Render in a moment.

---

## Part 2 — Render Setup

### 1. Push Code to GitHub

```bash
cd insurance-reminder
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<your-username>/insurance-reminder.git
git push -u origin main
```

### 2. Create the Web Service

1. Sign in to [render.com](https://render.com)
2. **New +** → **Web Service**
3. Connect your GitHub → select the repo
4. Render auto-detects `render.yaml` — review the config
5. Click **Apply**

### 3. Set Environment Variables

In the Render dashboard → your service → **Environment**:

| Key | Value |
|---|---|
| `DATABASE_URL` | (paste from Supabase) |
| `SUPABASE_URL` | (paste from Supabase) |
| `SUPABASE_KEY` | (paste from Supabase) |

Render will redeploy automatically.

### 4. Deploy

- First build takes 5–10 minutes (downloads EasyOCR models)
- When **Live** → open the URL Render gives you (e.g. `insurance-reminder.onrender.com`)

---

## Free Tier Limitations

| Limitation | Workaround |
|---|---|
| Service sleeps after 15 min inactivity | First request takes ~30 s |
| 750 hours/month | Enough for one service |
| Ephemeral disk | Use Supabase for all persistence |

---

## Updating the App

Push any code change to GitHub → Render auto-redeploys.

```bash
git add .
git commit -m "Describe your change"
git push
```

---

## Troubleshooting

**EasyOCR fails to load** — bump Render plan to Starter ($7/mo), free tier RAM may be tight.

**Database connection error** — check `DATABASE_URL` format and that the password is correct.

**PDFs not persisting** — confirm the `pdfs` bucket exists in Supabase Storage.
