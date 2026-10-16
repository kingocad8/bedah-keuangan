# Bedah Keuangan — Web Artikel

Situs statis artikel lengkap Bedah Keuangan. Versi ringkas tiap artikel tayang sebagai carousel di Instagram **@bedahkeuangan**.

## Struktur
```
web/
├── index.html                  → beranda + daftar artikel
├── style.css                   → tema "Meja Bedah" (kertas kerja analis)
├── artikel/
│   ├── thp-potongan-gaji.html
│   ├── bsu-900rb-2026.html
│   └── investasi-pemula.html
```

## Cara deploy ke Vercel (gratis, tanpa kartu)

1. **Buat repo GitHub baru**: nama `bedah-keuangan`, public. (github.com/new)
2. **Upload isi folder `web/`** ke repo — drag & drop lewat web GitHub, atau via browser.
3. **Vercel**: vercel.com → Add New Project → Import repo `bedah-keuangan` → Deploy.
4. Jadi: `https://bedah-keuangan.vercel.app` 🎉
5. Tiap artikel baru: tambah file di `artikel/`, tambah card di `index.html`, push → Vercel auto-deploy.

## Alur kerja per topik
1. Riset 1x (sumber terverifikasi 2–3 sumber) → tulis artikel lengkap di `artikel/` (dengan teori + ref-box)
2. Distilasi jadi carousel 10 slide untuk IG (di `../desain-v2/`)
3. Fokus konten awal: keuangan pribadi & keluarga (bukan UMKM)
