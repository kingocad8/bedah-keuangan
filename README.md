# Meja Bedah v2 — render pipeline (Bedah Keuangan)

Dunia visual: **selembar kertas kerja analis** (kertas `#FAF6EE` + garis
ledger, tinta `#0B3B3B`, amber `#E8A33D`, merah `#C0392B` hanya untuk
negatif/rugi). Angka tampilan selalu DejaVu Sans Mono Bold; headline
InterTight ExtraBold. Konsep lengkap: `../KONSEP-MEJA-BEDAH.md`.

Pipeline ini **reusable**: 1 modul bersama + 1 script render per reel.
Bukan script sekali pakai (perintah Oemar 11 Nov 2026).

## Struktur

```
reels/meja-bedah-v2/
  meja_bedah_v2.py          # modul bersama: kanvas, header, footer, headline,
                            #   ledger box, pill ILUSTRASI, panah, anotasi, dsb.
  fonts/                    # InterTight Regular/Bold/ExtraBold (OFL, Google Fonts)
  lifestyle-creep/
    render_lifestyle_creep.py   # 8 fungsi beat + main; QC angka via assert
    frames/beat-01.png ... beat-08.png
    README.md                   # catatan reel: beat, angka, caption
```

## Cara render

```bash
python3 lifestyle-creep/render_lifestyle_creep.py            # semua 8 beat
python3 lifestyle-creep/render_lifestyle_creep.py --beat 6   # 1 beat saja
```

Kebutuhan: Python 3 + Pillow (`pip install pillow`). Mono font diambil dari
sistem (`/usr/share/fonts/truetype/dejavu/DejaVuSansMono*.ttf`).

## Aturan QC (mengikat semua reel)

1. **Angka dicek ulang di kode** — `render_*.py` wajib punya `assert` untuk
   tiap hitungan simulasi (orde-magnitude juta vs miliar vs triliun).
2. **Simulasi = ILUSTRASI** — pill `ILUSTRASI`, BUKAN stempel `✓ TERVERIFIKASI`
   (angka ilustratif dilarang pakai stempel itu).
3. **Tiap beat visualnya beda** — angka jadi objek visual (balok/kolom/garis),
   bukan baris teks polos.
4. **Hook di detik 1–2** — beat 1 = headline hook, langsung terbaca.
5. **Tiap frame dicek visual** sebelum diserahkan: tanpa teks terpotong,
   tanpa tabrakan, tanpa teks lewat margin kanan. `pill_ilustrasi()` mengecilkan
   catatan otomatis (min 24px) supaya tidak pernah lewat margin.
6. **Maks 1 lingkaran anotasi** per frame; merah hanya untuk negatif/rugi.

## Reel baru

Salin folder `lifestyle-creep/` jadi `<topik>/`, ganti 8 fungsi beat +
angka QC + `README.md`. Modul `meja_bedah_v2.py` dipakai apa adanya;
helper baru yang generik masuk ke modul, bukan ke script reel.
