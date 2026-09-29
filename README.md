---
title: Argos Translate EN-ID
emoji: 🇮🇩
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Argos Translate EN → ID

Layanan penerjemah judul Inggris → Bahasa Indonesia, 100% offline (Argos Translate), tanpa API key, tanpa database.

> **Status: OPSIONAL.** news-app-web sekarang memakai terjemahan bawaan browser dan **tidak lagi membutuhkan layanan ini**. Repo ini disimpan sebagai alternatif bila suatu saat ingin terjemahan server-side.

## Endpoint

| Method | Path | Body | Keterangan |
|---|---|---|---|
| POST | `/translate` | `{"items":[{"id":"a1","text":"Oil rises","lang":"en"}]}` | Balas `{"items":[{"id":"a1","text":"Minyak naik"}],"engine":"argos"}` |
| GET | `/health` | — | Status model |

- Item dengan `lang:"id"` dilewati (tidak diterjemahkan ulang).
- Maksimal 60 item per permintaan (atur via env `MAX_ITEMS`).
- CORS terbuka default; batasi via env `ALLOWED_ORIGINS=https://domain-anda.vercel.app`.

## Deploy

### Hugging Face Spaces (gratis, tanpa kartu kredit)
1. Buah Space baru → pilih **Docker** → Space name bebas (mis. `news-translate`)
2. Upload semua file repo ini (atau hubungkan repo GitHub ini)
3. Tunggu build selesai (model diunduh saat build)
4. URL service: `https://NAMA-SPACE.hf.space/translate`

### Render (gratis)
1. New → **Web Service** → hubungkan repo GitHub ini
2. Environment: **Docker** (Dockerfile otomatis terpakai), instance **Free**
3. URL service: `https://nama-service.onrender.com/translate`

Catatan free tier: layanan "tidur" saat idle ±15 menit → permintaan pertama setelah tidur butuh ±30–60 detik untuk bangun. Frontend sudah menangani dengan cache di browser.

## Uji cepat

```bash
curl -X POST https://NAMA-SPACE.hf.space/translate \
  -H "Content-Type: application/json" \
  -d '{"items":[{"id":"t1","text":"Stocks fall as inflation rises","lang":"en"}]}'
```

Lalu set env var `TRANSLATE_URL` di project Vercel `news-app-web` ke URL `/translate` tersebut.
