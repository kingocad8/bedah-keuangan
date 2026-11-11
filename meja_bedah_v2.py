"""Meja Bedah v2 — shared render module (reusable across reels).

Dunia visual: selembar kertas kerja analis (KONSEP-MEJA-BEDAH.md).
Kanvas reels 1080x1920. Palet dikunci; MERAH hanya untuk negatif/rugi;
AMBER hanya untuk sorotan/angka kunci; maks 1 lingkaran anotasi per frame.
Angka tampilan selalu DejaVu Sans Mono Bold; headline InterTight ExtraBold.

Font: InterTight TTF dibundel di ./fonts (OFL, Google Fonts).
Mono: DejaVu Sans Mono sistem (/usr/share/fonts).

Aturan QC (dari naskah + reel_production_checks):
- Angka simulasi = ILUSTRASI -> pill ILUSTRASI, BUKAN stempel ✓ TERVERIFIKASI.
- Setiap frame dicek visual sebelum diserahkan (overlap, teks terpotong, tabrakan).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
M = 80                      # margin
CW = W - 2 * M              # lebar konten = 920

KERTAS = (250, 246, 238)    # #FAF6EE
TINTA = (11, 59, 59)        # #0B3B3B
AMBER = (232, 163, 61)      # #E8A33D
MERAH = (192, 57, 43)       # #C0392B
ARANG = (74, 85, 85)        # #4A5555
GARIS = (233, 224, 203)     # #E9E0CB
FOOT = (110, 119, 119)

FONTS_DIR = Path(__file__).resolve().parent / "fonts"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


# ---------------------------------------------------------------- font ----
def fi(weight, size):
    """InterTight. weight: Regular | Bold | ExtraBold."""
    return ImageFont.truetype(str(FONTS_DIR / f"InterTight-{weight}.ttf"), size)


def fm(bold, size):
    return ImageFont.truetype(MONO_B if bold else MONO, size)


def fit_mono_bold(text, size, max_w):
    while size > 20 and ImageFont.truetype(MONO_B, size).getlength(text) > max_w:
        size -= 2
    return ImageFont.truetype(MONO_B, size)


def fit_inter(weight, text, size, max_w):
    while size > 20 and ImageFont.truetype(
            str(FONTS_DIR / f"InterTight-{weight}.ttf"), size).getlength(text) > max_w:
        size -= 2
    return ImageFont.truetype(str(FONTS_DIR / f"InterTight-{weight}.ttf"), size)


def center(d, cx, y, text, font, fill):
    d.text((cx - d.textlength(text, font=font) / 2, y), text, font=font, fill=fill)


def right(d, x, y, text, font, fill):
    d.text((x - d.textlength(text, font=font), y), text, font=font, fill=fill)


def wrap(d, text, font, max_w):
    """Bungkus teks jadi beberapa baris agar muat max_w. Kembalikan list baris."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fmt_idr(n):
    """1_000_000 -> 'Rp1.000.000' (tanpa spasi, format naskah)."""
    return "Rp" + f"{n:,}".replace(",", ".")


# -------------------------------------------------------------- canvas ----
def new_canvas():
    img = Image.new("RGB", (W, H), KERTAS)
    d = ImageDraw.Draw(img)
    for y in range(96, H, 96):
        d.line([(0, y), (W, y)], fill=GARIS, width=2)
    return img, d


def header(d, rubrik, beat, total=8):
    """Tab rubrik + nomor beat + hairline. Kembalikan y konten (=190)."""
    f_tab = fi("Bold", 30)
    tw = d.textlength(rubrik, font=f_tab)
    d.rounded_rectangle([M, 64, M + tw + 60, 122], radius=10, fill=TINTA)
    d.text((M + 30, 76), rubrik, font=f_tab, fill=KERTAS)
    f_n = fm(False, 28)
    t = f"BEAT {beat}/{total}"
    d.text((W - M - d.textlength(t, font=f_n), 78), t, font=f_n, fill=ARANG)
    d.line([(M, 150), (W - M, 150)], fill=TINTA, width=3)
    return 190


def footer(d, beat):
    """@bedahkeuangan kiri; LEMBAR 0n/10 kanan (kerangka 10 slide, konsep)."""
    d.text((M, H - 100), "@bedahkeuangan", font=fm(False, 28), fill=ARANG)
    t = f"LEMBAR {beat:02d}/10"
    d.text((W - M - d.textlength(t, font=fm(False, 28)), H - 100),
           t, font=fm(False, 28), fill=ARANG)


# -------------------------------------------------------------- blok teks --
def headline(d, lines, y, size=88, lh=100):
    """lines: list (teks, warna). Kembalikan y setelah baris terakhir."""
    for text, fill in lines:
        f = fit_inter("ExtraBold", text, size, CW)
        d.text((M, y), text, font=f, fill=fill)
        y += lh
    return y


def subhead(d, text, y, size=38, fill=ARANG):
    """Satu/duabaris InterTight Regular. Kembalikan y setelah blok."""
    f = fi("Regular", size)
    for ln in wrap(d, text, f, CW):
        d.text((M, y), ln, font=f, fill=fill)
        y += size + 14
    return y


def ledger_lines(d, y, lines, size=44):
    """Kotak ledger berisi baris-baris mono bold + double-rule bawah.

    lines: list teks, atau (teks, warna) per baris.
    Mengikuti geometri sampel beat 6: tinggi 150 utk 2 baris, baris di
    y+18 + i*62. Untuk n baris lain, tinggi menyesuaikan.
    Kembalikan y setelah kotak.
    """
    h = 18 + len(lines) * 62 + 14
    d.rectangle([M, y, W - M, y + h], outline=TINTA, width=3)
    for i, ln in enumerate(lines):
        text, fill = ln if isinstance(ln, tuple) else (ln, TINTA)
        f = fit_mono_bold(text, size, CW - 40)
        d.text((M + 20, y + 18 + i * 62), text, font=f, fill=fill)
    d.line([(M, y + h - 8), (W - M, y + h - 8)], fill=TINTA, width=3)
    return y + h


def ledger_rows(d, y, rows, label_size=36, value_size=44, row_h=84, pad=24):
    """Kotak ledger label-kiri / angka-kanan.

    rows: list (label, nilai, warna_nilai). Kembalikan y setelah kotak.
    """
    h = pad * 2 + len(rows) * row_h
    d.rectangle([M, y, W - M, y + h], outline=TINTA, width=3)
    for i, (label, value, vfill) in enumerate(rows):
        ry = y + pad + i * row_h
        d.text((M + 24, ry + 8), label, font=fi("Bold", label_size), fill=TINTA)
        f = fit_mono_bold(value, value_size, CW // 2)
        right(d, W - M - 24, ry + 4, value, f, vfill)
        if i < len(rows) - 1:
            d.line([(M + 24, ry + row_h - 6), (W - M - 24, ry + row_h - 6)],
                   fill=GARIS, width=2)
    d.line([(M, y + h - 8), (W - M, y + h - 8)], fill=TINTA, width=3)
    return y + h


def pill_ilustrasi(d, x, y, note=None, note_size=32):
    """Pill ILUSTRASI (outline amber) + catatan opsional di kanannya.

    Dipakai di setiap frame yang menampilkan angka turunan dari angka hook
    (naskah: semua angka turunan = ILUSTRASI). Catatan dikecilkan otomatis
    (min 24px) supaya tidak pernah lewat margin kanan.
    Kembalikan (x_akhir, y+56).
    """
    pill = "ILUSTRASI"
    fp = fm(True, 30)
    pw = d.textlength(pill, font=fp) + 44
    d.rounded_rectangle([x, y, x + pw, y + 56], radius=28, outline=AMBER, width=4)
    d.text((x + 22, y + 12), pill, font=fp, fill=AMBER)
    if note:
        size = note_size
        f = fi("Regular", size)
        avail = (W - M) - (x + pw + 20)
        while size > 24 and d.textlength(note, font=f) > avail:
            size -= 2
            f = fi("Regular", size)
        # +10 di ukuran default = posisi sampel beat 6 yang di-ACC;
        # bila mengecil, pusatkan vertikal di pill 56px.
        ny = y + 10 if size == note_size else y + (56 - size) // 2
        d.text((x + pw + 20, ny), note, font=f, fill=ARANG)
    return x + pw, y + 56


def text_block(d, x, y, text, size=32, max_w=CW, fill=ARANG, weight="Regular"):
    """Teks terbungkus mulai di (x, y), lebar maks max_w (untuk kolom).

    Kembalikan y setelah blok. Dipakai untuk teks di kolom kanan dsb.
    """
    f = fi(weight, size)
    for ln in wrap(d, text, f, max_w):
        d.text((x, y), ln, font=f, fill=fill)
        y += size + 14
    return y


def pill_generic(d, x, y, text, fill=None, text_fill=TINTA, outline=None,
                 size=30):
    """Pill generik (mis. CTA). Kembalikan lebar pill."""
    fp = fm(True, size)
    pw = d.textlength(text, font=fp) + 48
    d.rounded_rectangle([x, y, x + pw, y + 56], radius=28,
                        fill=fill, outline=outline, width=4 if outline else 1)
    d.text((x + 24, y + 12), text, font=fp, fill=text_fill)
    return pw


def summary_rule(d, y, text, size=52):
    """Blok ringkasan: rule atas, teks mono bold, rule bawah (gaya sampel)."""
    d.line([(M, y), (W - M, y)], fill=TINTA, width=3)
    f = fit_mono_bold(text, size, CW)
    d.text((M, y + 18), text, font=f, fill=TINTA)
    d.line([(M, y + 92), (W - M, y + 92)], fill=TINTA, width=3)
    return y + 118


# -------------------------------------------------------------- bentuk ----
def arrow_down(d, cx, y0, y1, fill=TINTA, w=5, head=22):
    d.line([(cx, y0), (cx, y1 - head)], fill=fill, width=w)
    d.polygon([(cx - head, y1 - head), (cx + head, y1 - head), (cx, y1)], fill=fill)


def arrow_right(d, x0, x1, cy, fill=TINTA, w=5, head=20):
    d.line([(x0, cy), (x1 - head, cy)], fill=fill, width=w)
    d.polygon([(x1 - head, cy - head), (x1 - head, cy + head), (x1, cy)], fill=fill)


def circle_annotation(d, cx, cy, rx, ry, outline=AMBER, width=6):
    """1 lingkaran anotasi spidol per frame, maks 1x pakai."""
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=outline, width=width)


def hbar(d, x, y, w, h, fill=None, outline=None, width=0):
    if fill is not None:
        d.rectangle([x, y, x + w, y + h], fill=fill)
    if outline is not None:
        d.rectangle([x, y, x + w, y + h], outline=outline, width=width or 3)
