"""Meja Bedah v2 — render 8 beat lifestyle creep (hari-04).

Sumber naskah: reels/batch-nov-2026/hari-04-lifestyle-creep.md
Sampel ACC: desain-v2/sampel-v2-lifestyle-creep/render_beat6_v2.py
  (beat 6 di-porting 1:1 dari sampel yang di-ACC Oemar 11 Nov 2026 —
  JANGAN di-redesign; geometri + teksnya dipertahankan.)

QC ANGKA (ditegaskan di sini, render gagal bila salah):
  kenaikan   = Rp2.000.000 / bln   (angka hook dari brief, BUKAN survei)
  setengah    = Rp2.000.000 / 2    = Rp1.000.000 / bln
  5 tahun     = 60 bln;  Rp1.000.000 x 60 = Rp60.000.000 (tanpa imbal hasil)
  tanpa aturan = Rp0;   selisih = Rp60.000.000 - Rp0 = Rp60.000.000
  per tahun   = Rp12.000.000; kumulatif Thn 1-5 = 12/24/36/48/60 jt
Semua angka turunan = ILUSTRASI (pill ILUSTRASI, BUKAN stempel TERVERIFIKASI).

Pemakaian:
  python3 render_lifestyle_creep.py            # render 8 beat ke frames/
  python3 render_lifestyle_creep.py --beat 3   # render 1 beat saja
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from meja_bedah_v2 import (  # noqa: E402
    AMBER, ARANG, CW, FOOT, GARIS, H, KERTAS, M, MERAH, TINTA, W,
    arrow_down, center, circle_annotation, fi, fm, fit_inter,
    fit_mono_bold, footer, hbar, header, headline, ledger_lines,
    ledger_rows, new_canvas, pill_generic, pill_ilustrasi, right,
    subhead, summary_rule, text_block, wrap,
)

RUBRIK = "LIFESTYLE CREEP"
OUT = Path(__file__).resolve().parent / "frames"

# ------------------------------------------------------------ QC angka ----
KENAIKAN = 2_000_000
SETENGAH = KENAIKAN // 2
BULAN = 60
TOTAL_5THN = SETENGAH * BULAN
PER_TAHUN = SETENGAH * 12
KUMULATIF = [PER_TAHUN * (i + 1) // 1_000_000 for i in range(5)]

assert SETENGAH == 1_000_000, SETENGAH
assert TOTAL_5THN == 60_000_000, TOTAL_5THN
assert PER_TAHUN == 12_000_000, PER_TAHUN
assert KUMULATIF == [12, 24, 36, 48, 60], KUMULATIF
assert TOTAL_5THN - 0 == 60_000_000


def base(beat):
    img, d = new_canvas()
    y = header(d, RUBRIK, beat)
    return img, d, y


def finish(img, d, beat, name):
    footer(d, beat)
    out = OUT / name
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"saved {out} {img.size}")
    return out


# --------------------------------------------------------------- beat 1 ---
def beat1():
    """HOOK detik 1-2: dua angka raksasa berlawanan — gaji naik vs tabungan nol."""
    img, d, y = base(1)
    y = headline(d, [("GAJI NAIK 2 JUTA,", TINTA),
                     ("TABUNGAN", TINTA),
                     ("TETAP NOL?", AMBER)], y)
    y = subhead(d, "Kenapa bisa begitu? Bedah di meja ini.", y + 12)
    # bar 1: gaji naik — balok amber penuh
    y = 660
    d.text((M, y), "GAJI NAIK", font=fi("Bold", 40), fill=TINTA)
    hbar(d, M, y + 50, W - 2 * M, 170, fill=AMBER)
    f = fit_mono_bold("+Rp2.000.000", 80, W - 2 * M - 60)
    center(d, W // 2, y + 50 + 45, "+Rp2.000.000", f, KERTAS)
    center(d, W // 2, y + 260, "LARINYA KE MANA?", fm(True, 30), ARANG)
    # bar 2: tabungan — balok kosong bergaris merah
    y = 990
    d.text((M, y), "TABUNGAN", font=fi("Bold", 40), fill=TINTA)
    hbar(d, M, y + 50, W - 2 * M, 170, outline=MERAH, width=5)
    f0 = fit_mono_bold("Rp0", 120, W - 2 * M - 60)
    center(d, W // 2, y + 50 + 25, "Rp0", f0, MERAH)
    circle_annotation(d, W // 2, y + 50 + 85, 240, 105)
    summary_rule(d, 1400, "GAJI NAIK 2 JUTA — TABUNGAN NOL")
    pill_ilustrasi(d, M, 1544, "Angka hook — contoh, bukan survei.")
    return finish(img, d, 1, "beat-01.png")


# --------------------------------------------------------------- beat 2 ---
def beat2():
    """Gaya hidup naik duluan: 3 jalur bocor + ledger masuk/keluar/sisa."""
    img, d, y = base(2)
    y = headline(d, [("GAJI NAIK,", TINTA),
                     ("GAYA HIDUP", TINTA),
                     ("NAIK DULUAN.", AMBER)], y)
    y = subhead(d, "Kopi naik kelas, langganan nambah, cicilan baru muncul.",
                y + 12)
    rows = [("KOPI", "naik kelas"),
            ("LANGGANAN", "nambah terus"),
            ("CICILAN", "baru muncul")]
    ry = 690
    for label, sub in rows:
        hbar(d, M, ry, 14, 110, fill=MERAH)
        d.text((M + 34, ry - 6), label, font=fi("Bold", 42), fill=TINTA)
        d.text((M + 34, ry + 48), sub, font=fi("Regular", 32), fill=ARANG)
        # segitiga "bocor" (turun) di kanan
        cx = W - M - 40
        d.polygon([(cx - 26, ry + 8), (cx + 26, ry + 8), (cx, ry + 56)],
                  fill=MERAH)
        ry += 180
    y = ledger_lines(d, 1260, [("MASUK    +Rp2.000.000", TINTA),
                               ("KELUAR   -Rp2.000.000", MERAH),
                               ("SISA     Rp0", MERAH)])
    pill_ilustrasi(d, M, 1560, "Kenaikan habis tanpa jejak — contoh dari hook.")
    return finish(img, d, 2, "beat-02.png")


# --------------------------------------------------------------- beat 3 ---
def beat3():
    """Definisi: dua garis naik — pengeluaran lebih cepat dari penghasilan."""
    img, d, y = base(3)
    y = headline(d, [("LIFESTYLE", TINTA),
                     ("CREEP", AMBER)], y)
    y = subhead(d, "Pengeluaran naik secepat penghasilan — bahkan lebih cepat.",
                y + 12)
    # legenda
    ly = 620
    d.line([(M, ly + 14), (M + 60, ly + 14)], fill=TINTA, width=6)
    d.ellipse([M + 24, ly + 8, M + 36, ly + 20], fill=AMBER)
    d.text((M + 76, ly), "PENGHASILAN", font=fm(True, 30), fill=TINTA)
    d.line([(M + 400, ly + 14), (M + 460, ly + 14)], fill=MERAH, width=6)
    d.ellipse([M + 424, ly + 8, M + 436, ly + 20], fill=MERAH)
    d.text((M + 476, ly), "PENGELUARAN", font=fm(True, 30), fill=MERAH)
    # area grafik
    base_y = 1330
    d.line([(M, base_y), (W - M, base_y)], fill=TINTA, width=3)
    gaji = [(160, 1230), (360, 1180), (560, 1120), (760, 1050), (960, 980)]
    keluar = [(160, 1230), (360, 1140), (560, 1030), (760, 880), (960, 700)]
    d.line(gaji, fill=TINTA, width=6, joint="curve")
    for x, yy in gaji:
        d.ellipse([x - 9, yy - 9, x + 9, yy + 9], fill=AMBER)
    d.line(keluar, fill=MERAH, width=6, joint="curve")
    for x, yy in keluar:
        d.ellipse([x - 9, yy - 9, x + 9, yy + 9], fill=MERAH)
    circle_annotation(d, 960, 700, 100, 66)
    right(d, W - M, base_y + 24, "WAKTU →", fm(False, 28), ARANG)
    y = subhead(d, "Standar \u2018kebutuhan\u2019 ikut bergeser tiap gaji naik.",
                1460, size=34)
    return finish(img, d, 3, "beat-03.png")


# --------------------------------------------------------------- beat 4 ---
def beat4():
    """Aturan setengah kenaikan: balok Rp2 jt dibelah 50/50."""
    img, d, y = base(4)
    y = headline(d, [("ATURAN SETENGAH", TINTA),
                     ("KENAIKAN", TINTA)], y)
    y = subhead(d, "Setengah kenaikan langsung pindah ke tabungan — "
                   "otomatis di hari gajian.", y + 12)
    # balok belah dua
    by, bh = 680, 180
    half = (W - 2 * M) // 2
    hbar(d, M, by, half, bh, fill=AMBER)
    hbar(d, M + half, by, half, bh, outline=TINTA, width=4)
    f50 = fit_mono_bold("50%", 72, half - 40)
    center(d, M + half // 2, by + 54, "50%", f50, KERTAS)
    center(d, M + half + half // 2, by + 54, "50%", f50, TINTA)
    center(d, M + half // 2, by + bh + 22, "TABUNGAN OTOMATIS",
           fi("Bold", 34), TINTA)
    center(d, M + half + half // 2, by + bh + 22, "BOLEH DINIKMATI",
           fi("Bold", 34), TINTA)
    y = ledger_lines(d, 990, ["Rp2.000.000 ÷ 2 = Rp1.000.000 / bln"])
    # stempel: otomatis di hari gajian
    sy = 1180
    d.rectangle([M, sy, W - M, sy + 110], fill=TINTA)
    center(d, W // 2, sy + 30, "OTOMATIS DI HARI GAJIAN", fi("Bold", 44),
           KERTAS)
    summary_rule(d, 1400, "SETENGAH DITABUNG — SETENGAH DINIKMATI")
    pill_ilustrasi(d, M, 1560, "50% dari panduan; angka rupiah contoh hook.")
    return finish(img, d, 4, "beat-04.png")


# --------------------------------------------------------------- beat 5 ---
def beat5():
    """Bayar diri sendiri dulu: aliran vertikal gajian → tabungan → hidup."""
    img, d, y = base(5)
    y = headline(d, [("BAYAR DIRI", TINTA),
                     ("SENDIRI DULU", AMBER)], y)
    y = subhead(d, "Baru sisanya untuk hidup — supaya tidak merasa tersiksa.",
                y + 12)
    # kotak 1: gajian
    by, bh = 620, 190
    d.rectangle([M, by, W - M, by + bh], outline=TINTA, width=4)
    center(d, W // 2, by + 28, "GAJIAN", fi("Bold", 40), TINTA)
    center(d, W // 2, by + 88, "Rp2.000.000",
           fit_mono_bold("Rp2.000.000", 60, W - 2 * M - 60), TINTA)
    arrow_down(d, W // 2, by + bh + 8, by + bh + 58)
    # kotak 2: tabungan dulu (amber)
    by2, bh2 = 876, 240
    d.rectangle([M, by2, W - M, by2 + bh2], fill=AMBER)
    center(d, W // 2, by2 + 30, "TABUNGAN DULU", fi("Bold", 44), KERTAS)
    center(d, W // 2, by2 + 94, "Rp1.000.000",
           fit_mono_bold("Rp1.000.000", 64, W - 2 * M - 60), KERTAS)
    center(d, W // 2, by2 + 184, "otomatis", fi("Regular", 30), KERTAS)
    arrow_down(d, W // 2, by2 + bh2 + 8, by2 + bh2 + 58)
    # kotak 3: sisanya untuk hidup
    by3, bh3 = 1182, 220
    d.rectangle([M, by3, W - M, by3 + bh3], outline=TINTA, width=4)
    center(d, W // 2, by3 + 28, "SISANYA UNTUK HIDUP", fi("Bold", 40), TINTA)
    center(d, W // 2, by3 + 88, "Rp1.000.000",
           fit_mono_bold("Rp1.000.000", 60, W - 2 * M - 60), TINTA)
    center(d, W // 2, by3 + 168, "boleh dinikmati", fi("Regular", 30), ARANG)
    pill_ilustrasi(d, M, 1490, "Setengah kenaikan = Rp1.000.000/bln.")
    return finish(img, d, 5, "beat-05.png")


# --------------------------------------------------------------- beat 6 ---
def beat6():
    """Simulasi — PORT 1:1 dari sampel ACC (render_beat6_v2.py). JANGAN ubah."""
    img, d, y = base(6)
    y = headline(d, [("KENAIKAN 2 JUTA,", TINTA),
                     ("SETENGAHNYA", TINTA),
                     ("JADI 60 JUTA.", AMBER)], y)
    # Subhead sampel: 1 baris di y=502 (sampel 38px = 964px, 44px lewat
    # margin kanan — diperbaiki QC jadi 36px = 913px, muat di 920px,
    # tanpa menggeser alur y sampel: y lanjut 564 seperti aslinya).
    d.text((M, y + 12), "Aturan setengah kenaikan — tabung otomatis di hari gajian.",
           font=fi("Regular", 36), fill=ARANG)
    y = y + 12 + 62
    # hitungan ledger (geometri sampel: kotak 150, baris di +18 + i*62)
    box_y0, box_y1 = y, y + 150
    d.rectangle([M, box_y0, W - M, box_y1], outline=TINTA, width=3)
    for i, ln in enumerate(["Rp2.000.000 ÷ 2 = Rp1.000.000 / bln",
                            "Rp1.000.000 × 60 bln = Rp60.000.000"]):
        f = fit_mono_bold(ln, 44, W - 2 * M - 40)
        d.text((M + 20, box_y0 + 18 + i * 62), ln, font=f, fill=TINTA)
    d.line([(M, box_y1 - 8), (W - M, box_y1 - 8)], fill=TINTA, width=3)
    y = box_y1 + 44
    # dua kolom perbandingan
    col_w = 440
    lx, rx = M, W - M - col_w
    col_y0, col_y1 = y, y + 640
    # kiri: TANPA ATURAN (merah)
    d.rectangle([lx, col_y0, lx + col_w, col_y1], outline=MERAH, width=4)
    d.rectangle([lx, col_y0, lx + col_w, col_y0 + 72], fill=MERAH)
    center(d, lx + col_w / 2, col_y0 + 16, "TANPA ATURAN", fi("Bold", 34), KERTAS)
    f0 = fit_mono_bold("Rp0", 120, col_w - 40)
    center(d, lx + col_w / 2, col_y0 + 110, "Rp0", f0, MERAH)
    center(d, lx + col_w / 2, col_y0 + 250, "kenaikan habis", fi("Regular", 34),
           ARANG)
    center(d, lx + col_w / 2, col_y0 + 292, "jadi nol", fi("Regular", 34), ARANG)
    for i in range(5):
        by = col_y0 + 360 + i * 48
        d.rectangle([lx + 40, by, lx + col_w - 40, by + 30], outline=MERAH,
                    width=2)
        d.text((lx + 56, by + 2), f"Thn {i + 1}", font=fm(False, 22), fill=MERAH)
        d.text((lx + col_w - 130, by + 2), "Rp0", font=fm(True, 22), fill=MERAH)
    # kanan: ATURAN SETENGAH (amber/tinta)
    d.rectangle([rx, col_y0, rx + col_w, col_y1], outline=TINTA, width=4)
    d.rectangle([rx, col_y0, rx + col_w, col_y0 + 72], fill=TINTA)
    center(d, rx + col_w / 2, col_y0 + 16, "ATURAN SETENGAH", fi("Bold", 34),
           KERTAS)
    f1 = fit_mono_bold("Rp60.000.000", 46, col_w - 60)
    center(d, rx + col_w / 2, col_y0 + 104, "Rp60.000.000", f1, TINTA)
    center(d, rx + col_w / 2, col_y0 + 168, "dalam 5 tahun", fi("Regular", 34),
           ARANG)
    cum = [12, 24, 36, 48, 60]
    for i in range(5):
        by = col_y0 + 232 + i * 56
        d.rectangle([rx + 40, by, rx + col_w - 110, by + 40], fill=AMBER)
        d.text((rx + col_w - 96, by + 6), f"{cum[i]} jt", font=fm(True, 26),
               fill=TINTA)
        d.text((rx + 56, by + 8), f"Thn {i + 1}  +Rp12 jt", font=fi("Bold", 24),
               fill=TINTA)
    ax, ay = rx + col_w / 2, col_y0 + 130
    d.ellipse([ax - 195, ay - 30, ax + 195, ay + 30], outline=AMBER, width=6)
    d.line([(lx + col_w + 8, col_y0 + 320), (rx - 8, col_y0 + 320)],
           fill=TINTA, width=5)
    d.polygon([(rx - 8, col_y0 + 300), (rx - 8, col_y0 + 340),
               (rx + 14, col_y0 + 320)], fill=TINTA)
    y = col_y1 + 44
    # ringkasan
    y = summary_rule(d, y, "SELISIH: Rp60.000.000")
    # sampel: pill langsung di y (1560), tanpa +26
    pill_ilustrasi(d, M, y, "Simulasi dari angka hook; tanpa imbal hasil.")
    return finish(img, d, 6, "beat-06.png")


# --------------------------------------------------------------- beat 7 ---
def beat7():
    """Affiliate: kartu sampul buku Atomic Habits + etalase link bio."""
    img, d, y = base(7)
    y = headline(d, [("BACAAN LANJUTAN:", TINTA),
                     ("ATOMIC HABITS", AMBER)], y)
    y = subhead(d, "Buku Atomic Habits bisa jadi bacaan lanjutannya.", y + 12)
    # kartu sampul buku (kiri)
    bx, by, bw, bh = M, 700, 400, 720
    d.rectangle([bx, by, bx + bw, by + bh], outline=TINTA, width=4)
    d.rectangle([bx, by, bx + bw, by + 16], fill=TINTA)
    center(d, bx + bw / 2, by + 200, "ATOMIC", fit_inter("ExtraBold", "ATOMIC", 64, bw - 60), TINTA)
    center(d, bx + bw / 2, by + 280, "HABITS", fit_inter("ExtraBold", "HABITS", 64, bw - 60), TINTA)
    d.line([(bx + 60, by + 380), (bx + bw - 60, by + 380)], fill=AMBER, width=6)
    center(d, bx + bw / 2, by + 420, "JAMES CLEAR", fm(True, 30), TINTA)
    center(d, bx + bw / 2, by + 470, "BUKU", fm(False, 28), ARANG)
    # pita penanda (bookmark) amber di kanan atas sampul
    d.rectangle([bx + bw - 70, by + 16, bx + bw - 26, by + 130], fill=AMBER)
    d.polygon([(bx + bw - 70, by + 130), (bx + bw - 26, by + 130),
               (bx + bw - 48, by + 104)], fill=KERTAS)
    # kolom kanan: etalase (semua teks di x=rx, lebar 460 — JANGAN pakai
    # subhead() full-width, itu yang dulu menabrak kartu buku)
    rx = M + bw + 60
    col_w = W - M - rx
    d.text((rx, 720), "CEK ETALASE", font=fi("Bold", 44), fill=TINTA)
    d.text((rx, 786), "LINK BIO", font=fit_mono_bold("LINK BIO", 72, col_w),
           fill=TINTA)
    d.line([(rx, 900), (W - M, 900)], fill=TINTA, width=3)
    pill_generic(d, rx, 940, "LINK MENYUSUL", outline=AMBER, text_fill=AMBER)
    text_block(d, rx, 1040, "Link affiliate menyusul — cek etalase di link bio.",
               size=32, max_w=col_w)
    d.text((rx, 1200), "Kenapa nyambung?", font=fi("Bold", 32), fill=TINTA)
    text_block(d, rx, 1244, "Kebiasaan otomatis = inti solusi video ini.",
               size=32, max_w=col_w)
    # penutup: kredit buku, tengah, di bawah blok
    center(d, W // 2, 1520, "ATOMIC HABITS — JAMES CLEAR",
           fit_mono_bold("ATOMIC HABITS — JAMES CLEAR", 36, CW), TINTA)
    return finish(img, d, 7, "beat-07.png")


# --------------------------------------------------------------- beat 8 ---
def beat8():
    """CTA komen: dua pilihan + kotak komentar."""
    img, d, y = base(8)
    y = headline(d, [("KENAIKAN GAJI", TINTA),
                     ("TERAKHIRMU", TINTA),
                     ("LARINYA KE MANA?", AMBER)], y)
    y = subhead(d, "Tulis di komen — tabungan atau gaya hidup?", y + 12)
    # dua kotak pilihan
    by, bh, bw = 680, 300, 440
    lx, rx = M, W - M - bw
    d.rectangle([lx, by, lx + bw, by + bh], fill=AMBER)
    center(d, lx + bw / 2, by + 90, "TABUNGAN",
           fit_mono_bold("TABUNGAN", 54, bw - 40), KERTAS)
    center(d, lx + bw / 2, by + 170, "disimpan dulu", fi("Regular", 30), KERTAS)
    d.rectangle([rx, by, rx + bw, by + bh], outline=TINTA, width=4)
    center(d, rx + bw / 2, by + 90, "GAYA HIDUP",
           fit_mono_bold("GAYA HIDUP", 48, bw - 40), TINTA)
    center(d, rx + bw / 2, by + 170, "dinikmati dulu", fi("Regular", 30), ARANG)
    # kotak komentar
    cy, ch = 1080, 170
    d.rectangle([M, cy, W - M, cy + ch], outline=TINTA, width=3)
    _ct = "Tulis di komen..."
    _cf = fi("Regular", 40)
    d.text((M + 28, cy + 56), _ct, font=_cf, fill=ARANG)
    _cx = M + 28 + d.textlength(_ct, font=_cf) + 14
    d.rectangle([_cx, cy + 62, _cx + 6, cy + 102], fill=AMBER)
    pill_generic(d, M, 1340, "TULIS DI KOMEN", fill=TINTA, text_fill=KERTAS)
    center(d, W // 2, 1470, "Share ke teman yang gajinya naik,",
           fi("Regular", 34), ARANG)
    center(d, W // 2, 1514, "tabungannya tetap nol.", fi("Regular", 34), ARANG)
    return finish(img, d, 8, "beat-08.png")


BEATS = {1: beat1, 2: beat2, 3: beat3, 4: beat4,
         5: beat5, 6: beat6, 7: beat7, 8: beat8}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--beat", type=int, choices=list(BEATS))
    args = ap.parse_args()
    targets = [args.beat] if args.beat else sorted(BEATS)
    for n in targets:
        BEATS[n]()
