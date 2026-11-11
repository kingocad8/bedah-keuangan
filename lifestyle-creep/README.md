# Lifestyle Creep — Meja Bedah v2 (8 beat, ~60 detik)

Naskah: `../../reels/batch-nov-2026/hari-04-lifestyle-creep.md` (ACC sampel
11 Nov 2026; pipeline repo atas perintah Oemar 11 Nov 2026).
Render: `python3 render_lifestyle_creep.py` → `frames/beat-01.png` … `beat-08.png`
(1080x1920). VO ElevenLabs + musik/SFX bukan bagian pipeline ini.

## Beat

| # | Visual (masing-masing beda) |
|---|---|
| 1 | HOOK detik 1–2: balok penuh amber `+Rp2.000.000` vs balok kosong merah `Rp0` (dilingkari) + ringkasan `GAJI NAIK 2 JUTA — TABUNGAN NOL` |
| 2 | 3 jalur bocor (KOPI / LANGGANAN / CICILAN, segitiga turun merah) + ledger `MASUK +Rp2.000.000 / KELUAR -Rp2.000.000 / SISA Rp0` |
| 3 | Grafik 2 garis naik: PENGELUARAN (merah, lebih curam, ujung dilingkari) vs PENGHASILAN (tinta); tanpa angka — skema definisi, bukan data |
| 4 | Balok `Rp2.000.000` dibelah 50/50 (`TABUNGAN OTOMATIS` vs `BOLEH DINIKMATI`) + ledger `÷ 2 = Rp1.000.000/bln` + stempel `OTOMATIS DI HARI GAJIAN` |
| 5 | Aliran vertikal: `GAJIAN Rp2.000.000` → `TABUNGAN DULU Rp1.000.000` (amber) → `SISANYA UNTUK HIDUP Rp1.000.000` |
| 6 | **Sampel ACC (port 1:1)** — ledger hitungan + 2 kolom `TANPA ATURAN Rp0` vs `ATURAN SETENGAH Rp60.000.000` + 5 balok tahun menumpuk (12/24/36/48/60 jt) + `SELISIH: Rp60.000.000` |
| 7 | Kartu sampul buku `ATOMIC HABITS — JAMES CLEAR` + kolom `CEK ETALASE / LINK BIO` + pill `LINK MENYUSUL` (tanpa URL) |
| 8 | CTA komen: 2 kotak pilihan `TABUNGAN` vs `GAYA HIDUP` + kotak komentar + pill `TULIS DI KOMEN` |

## QC angka (assert di `render_lifestyle_creep.py`)

- Kenaikan (hook, bukan survei): Rp2.000.000/bln
- Setengah: Rp2.000.000 ÷ 2 = Rp1.000.000/bln
- 5 tahun = 60 bln → Rp1.000.000 × 60 = **Rp60.000.000** (tanpa imbal hasil)
- Per tahun Rp12.000.000 → kumulatif Thn 1–5: 12 / 24 / 36 / 48 / 60 jt
- Tanpa aturan: Rp0; selisih: Rp60.000.000 − Rp0 = Rp60.000.000
- Semua angka turunan = **ILUSTRASI** (pill ILUSTRASI di beat 1, 2, 4, 5, 6).
  TIDAK ADA stempel `✓ TERVERIFIKASI` di frame mana pun.

## Beat 6 vs sampel ACC

`frames/beat-06.png` dibanding piksel-per-piksel dengan sampel yang di-ACC
(`desain-v2/sampel-v2-lifestyle-creep/meja-bedah-v2-lifestyle-creep-beat6.png`):
beda 15.025 dari 2.073.600 piksel (0,7%), semuanya di baris subhead —
perbaikan QC: subhead sampel 38px = 964px (44px lewat margin kanan) jadi
36px = 913px (muat di margin). Geometri lain identik.

## Caption (979 karakter, batas 2.200)

```
Gaji naik 2 juta, tabungan tetap nol — kenapa? Karena tiap gaji naik, gaya hidup naik duluan. Ini namanya lifestyle creep.

Solusinya: aturan setengah kenaikan. Begitu gaji naik, setengah kenaikannya langsung pindah ke tabungan otomatis di hari gajian. Bayar diri sendiri dulu, baru sisanya untuk hidup.

Simulasi ILUSTRASI: kenaikan 2 juta, setengahnya 1 juta ditabung tiap bulan, 5 tahun jadi 60 juta — tanpa menghitung imbal hasil apa pun. Tanpa aturan ini, kenaikan yang sama bisa habis jadi nol.

Sumber: panduan perencana keuangan tentang lifestyle inflation dan pay yourself first (detail di riset). Angka simulasi adalah ILUSTRASI dari angka hook, bukan survei kenaikan gaji — sesuaikan dengan kenaikan gajimu sendiri.

Buku kandidat di etalase link bio: Atomic Habits (James Clear) — link affiliate menyusul.

Tulis di komen, kenaikan gaji terakhir kamu larinya ke mana, ke tabungan atau ke gaya hidup?
#BedahKeuangan #LifestyleCreep #GajiNaik #Tabungan #KeuanganPribadi
```
