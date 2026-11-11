# QC — Lifestyle Creep v2 MOTION GRAPHICS (VO FINAL Senandika speed 110)

**Video:** `lifestyle-creep-v2-motion-test.mp4` — 61,87 dtk, 1080×1920, 30 fps, H.264, 4,3 MB.
**VO:** Senandika storytelling, Multilingual v2, stability 25 / style 60 / speed 110 (DIKUNCI Oemar 11 Nov 17:58).
**Segmen:** `work/v2-senandika-110/vo_segments.json` — 8 beat: 0–3,15 · 3,15–15,21 · 15,21–21,35 · 21,35–28,82 · 28,82–36,01 · 36,01–50,67 · 50,67–55,47 · 55,47–61,86.
**Musik:** "Driving Ambition" — Ahjay Stelino (Mixkit). **SFX:** whoosh di 7 batas beat, boom di t=0, shimmer di awal beat 8.
**Status:** BELUM diposting, BELUM masuk antrean autopilot. Menunggu verdict Oemar.

## 1. Spesifikasi teknis (ffprobe, terukur di file final)

| Item | Hasil | Target |
|---|---|---|
| Resolusi / fps | 1080×1920 / 30 | 1080×1920 / 30 ✓ |
| Durasi video | 61,87 dtk | ≈61,86 (VO) ✓ |
| Audio | AAC, stereo, 48 kHz, 192k | stereo 48 kHz ✓ |
| Mean volume (campuran) | −14,0 dB | VO ≈ −14 ✓ |
| Peak / true peak | −0,7 dB / −0,72 dBTP | ≤ −0,5 dB ✓ |
| Integrated loudness | −11,77 LUFS, LRA 2,0 | — |
| Musik di jeda VO (4 titik ukur) | −19,7 / −20,4 / −21,2 / −23,9 dB | −18 s.d. −22 dB — lihat catatan 4 |

## 2. QC frame (render `work/motion-frames/`, 1.950 frame)

- **Frame akhir ke-8 beat PIKSEL-IDENTIK dengan frame statis** (mean abs diff 0,0000) — desain v2 TIDAK berubah (warna/layout/teks/angka sama persis).
- Frame tengah animasi BERBEDA dari statis (motion terkonfirmasi): B1 f45 diff 6,11 · B2 f120 diff 3,94 · B4 f80 diff 17,48 · B6 f250 diff 7,29 · B8 f60 diff 1,89.
- Spot-check visual 3 frame tengah (b1/0045, b4/0080, b6/0250): teks tidak terpotong/tabrak; footer "LEMBAR nn/08" utuh di semua frame; count-up beat 6 terbaca bersih (Rp59.967.220 di tengah hitung naik).

## 3. QC sinkron frame↔VO (sampling dari video final)

| t (dtk) | Yang tampil | Yang diucap VO | Hasil |
|---|---|---|---|
| 1,5 | Bar amber "+Rp2.000.000" penuh, outline merah TABUNGAN tumbuh | "Gaji naik 2 juta…" | ✓ hook nendang di detik 1 |
| 3,4 | Transisi slideleft 1→2 di tengah jalan | Jeda mikro antar beat | ✓ transisi bergerak, bukan hard cut |
| 6,5 | Baris KOPI sudah muncul; LANGGANAN/CICILAN belum | "Kopi naik kelas" | ✓ baris mengikuti VO satu per satu |
| 24,0 | Balok amber penuh "50%" kiri; belah belum mulai (2,87) | "…setengah kenaikan…" | ✓ |
| 42,5 | Count-up Rp29.078.028 + balok Thn 1 tumbuh | "Lima tahun, itu jadi 60 juta rupiah" | ✓ hitung naik TEPAT di kalimat 60 juta |
| 58,0 | Kotak TABUNGAN + GAYA HIDUP + "Tulis di komen…" sudah terketik | "…larinya ke mana" | ✓ |

## 4. Deskripsi motion per beat (waktu relatif awal beat, VO speed 110)

- **Beat 1 (0–3,15, hook):** headline slide-up 0–0,59 (3 baris stagger); subhead 0,60; bar amber tumbuh 0,15–0,80 + count-up +Rp2.000.000 di 0,20–0,90; "LARINYA KE MANA?" 1,00; bar merah TABUNGAN pop 1,22–1,72 + "Rp0" pop 1,57 + elips merah digambar 1,77–2,22; summary 2,55; pill ILUSTRASI 2,80.
- **Beat 2 (3,15–15,21):** headline 0–0,95; baris KOPI 3,03 ("Kopi naik kelas"), LANGGANAN 4,53, CICILAN 5,84 — masing-masing bar merah tumbuh vertikal + label slide + segitiga pop; ledger 7,31 ("dan kenaikan itu habis tanpa jejak"); 3 baris ledger stagger 7,46/7,91/8,36; pill 10,03.
- **Beat 3 (15,21–21,35):** headline 0–0,90; garis PENGHASILAN digambar progresif 2,15; garis PENGELUARAN menyusul lebih curam 2,42 + titik-titik pop di vertex; lingkaran di ujung merah 4,91 ("bahkan lebih cepat"); "WAKTU" 5,21; subhead 5,31.
- **Beat 4 (21,35–28,82):** headline 0–0,90; balok amber tumbuh 1,87–2,57; "50%" kiri pop 2,55; wipe kertas + garis pembagi 2,87–3,37 (balok TERBELAH); "50%" kanan pop 3,19; label TABUNGAN OTOMATIS / BOLEH DINIKMATI 3,52; ledger 3,77; stempel "OTOMATIS DI HARI GAJIAN" slam 5,88 (di frasa "otomatis di hari gajian"); summary 6,63; pill 6,93.
- **Beat 5 (28,82–36,01):** headline 0–0,90; kotak GAJIAN pop 0; panah mengalir 0,45; kotak TABUNGAN DULU pop 0,91 (di tengah frasa "bayar diri sendiri dulu"); panah 1,36; kotak SISANYA pop 1,81 ("baru sisanya untuk hidup"); pill 4,07.
- **Beat 6 (36,01–50,67, info ditahan):** headline 0–0,90; baris ledger 1,68 + 3,64 (hitungan dibaca di frasa 0); kolom kanan ATURAN SETENGAH 5,90; count-up Rp0→Rp60.000.000 di 6,00–8,50 (TEPAT di frasa "Lima tahun, itu jadi 60 juta rupiah"); 5 balok tahun menumpuk 6,32–8,32; "dalam 5 tahun" 8,10; lingkaran 8,60; kolom kiri TANPA ATURAN 10,92 ("Tanpa aturan ini"); Rp0 pop 11,27; teks 11,57; 5 baris kosong stagger 11,87–12,84; panah antar-kolom 13,12; SELISIH: Rp60.000.000 13,47; pill 13,97.
- **Beat 7 (50,67–55,47):** headline 0–0,90; kartu buku slide dari kiri 0–1,50 + teks sampul pop + bookmark; kolom kanan slide 2,84 ("cek etalase di link bio"); CEK ETALASE 2,84, LINK BIO 3,09, garis 3,39, pill LINK MENYUSUL 3,69, teks 3,94, "Kenapa nyambung?" 4,19, teks ke-2 4,44, kredit 4,41.
- **Beat 8 (55,47–61,86, CTA):** headline 0–0,90; kotak TABUNGAN pop 0,30; kotak GAYA HIDUP pop 0,80; kotak komentar 0,90; teks mengetik "Tulis di komen…" 1,15–2,45 + kursor berkedip; pill "TULIS DI KOMEN" 3,20; baris share 4,09.

**Transisi antar beat (0,45 dtk, whoosh di tiap batas):** 1→2 slideleft · 2→3 slideup · 3→4 wipeleft · 4→5 slidedown · 5→6 slideleft · 6→7 fade · 7→8 slideup. Transisi menempati [batas, batas+0,45]; jam animasi beat baru mulai tepat di batas segmen (sinkron VO).

## 5. Catatan QC — yang belum sempurna / perlu diketahui

1. **Beat 5 dead zone ~3 dtk:** diagram lengkap di 2,16, pill di 4,07, lalu frame lengkap ditahan sampai beat berakhir (7,19) sementara VO menjelaskan "Setengah sisanya boleh dinikmati, supaya tidak merasa tersiksa". Bukan bug — tidak ada elemen baru yang bisa dimunculkan (semua sudah tampil). Sama di beat 2: headline selesai 0,95, baris KOPI baru di 3,03 (hold ~2 dtk pada headline — VO sedang mengucap kalimat pembuka).
2. **Beat 7 sangat padat (4,80 dtk):** "Kenapa nyambung?" (4,19) dan kredit (4,41) hampir bersamaan; teks ke-2 selesai 4,74 (0,06 dtk sebelum frame terakhir beat). Tidak ada tabrakan visual (area berbeda), tapi beat ini paling rapat.
3. **Musik di jeda:** 3 dari 4 titik ukur −19,7 s.d. −21,2 dB (dalam target −18 s.d. −22). Satu titik −23,9 dB (jeda 5,99–6,38) — di ekor release ducking 150 ms, tipis di bawah lantai −22 dB; tidak terdengar sebagai drop, bed tetap di bawah VO.
4. **Build gabungan sempat SIGSEGV sekali** (render speed-100, ffmpeg returncode −11, memori tersedia saat itu 1.633 MB; video-only dan audio-only terisolasi berhasil). Percobaan ulang dengan speed-110 BERHASIL (returncode 0). Bila crash terulang, fallback two-pass sudah teruji: render video-only → mux audio dengan rantai yang sama.
5. **Angka QC:** kenaikan 2.000.000; setengah 1.000.000; 60 bln → 60.000.000; per tahun 12.000.000; kumulatif 12/24/36/48/60 jt — semua cocok dengan naskah. Label ILUSTRASI dipakai di beat 4/6; TIDAK ADA stempel ✓ TERVERIFIKASI pada angka ilustratif.

## 6. Pipeline + cara re-render

- **Pipeline animasi:** `~/workspace/bedah-keuangan/desain-v2/meja-bedah-v2/animate_lifestyle_creep.py` (~1.050 baris; easing, layer pop/slide/fade, line-draw, count-up, typewriter; timing dari deteksi jeda VO via `silencedetect` + file segmen).
- **Build video:** `~/workspace/bedah-keuangan/reels/batch-nov-2026/lifestyle-creep-v2/work/build_motion.py` (rantai xfade 7 transisi + rantai audio dari `build_reel.py` — VO loudnorm, bed Driving Ambition, SFX).
- **Frame motion + manifest:** `work/motion-frames/b<1-8>/%04d.png` + `work/motion-frames/manifest.json` (frame counts, offset xfade, frasa per beat).
- **Re-render dari VO/segmen baru:**
  ```bash
  cd ~/workspace/bedah-keuangan/desain-v2/meja-bedah-v2
  python3 animate_lifestyle_creep.py --segments <path/vo_segments.json> --vo <path/vo_trimmed.wav> --out <folder-reel>/work/motion-frames
  cd <folder-reel>/work
  python3 build_motion.py --vo <path/vo_trimmed.wav> --segments <path/vo_segments.json> --out ../lifestyle-creep-v2-motion-test.mp4
  ```
  Timing TIDAK di-hardcode: semua jangkar elemen dibaca dari frasa yang terdeteksi di VO baru. Catatan: jangkar beat 2/4/6 memakai struktur frasa VO storytelling (headline 1 frasa; hitungan ledger di frasa 0 yang panjang) — bila VO baru strukturnya sangat berbeda, cek jadwal kering dulu (`animate_lifestyle_creep.py` mencetak frasa per beat; semua elemen harus selesai sebelum frame terakhir tiap beat).
- **Kode pipeline BELUM di-push ke repo** (branch `reels/meja-bedah-v2-lifestyle-creep`, file teks saja) — menunggu keputusan.
