"""Meja Bedah v2 — MOTION pipeline (animasi per elemen + transisi).

Latar: video v2 pertama DITOLAK Oemar 11 Nov 2026 ("kayak slide presentasi",
"malah downgrade") — 8 frame statis cuma di-zoom pelan, tanpa transisi dan
tanpa motion per elemen. Pipeline ini menganimasikan DESAIN YANG SAMA
(palet, layout, teks, angka — geometri di-porting 1:1 dari
render_lifestyle_creep.py, JANGAN di-redesign) per elemen mengikuti VO:
balok tumbuh, baris muncul satu per satu, garis digambar progresif, angka
menghitung naik (count-up), kartu/kotak masuk dengan hentakan.

Timing: pipeline membaca file segmen (vo_segments.json) + mendeteksi jeda
(silence) di file VO untuk membagi tiap beat jadi frasa. Elemen diikat ke
awal frasa (bukan ke detik absolut) — jadi VO baru dengan timing berbeda
tinggal di-render ulang dari file segmen + VO baru tanpa redesain.

Pemakaian:
  python3 animate_lifestyle_creep.py --segments <seg.json> --vo <vo.wav>
      [--out DIR] [--fps 30] [--transition 0.45] [--beat N]
  -> frame PNG per beat di OUT/b<n>/%04d.png + OUT/manifest.json
     (frame counts + offset xfade, dipakai build_motion.py)

QC ANGKA (sama seperti render statis — render gagal bila salah):
  kenaikan 2jt; setengah 1jt/bln; 60 bln -> Rp60.000.000 (tanpa imbal hasil);
  tanpa aturan Rp0; selisih Rp60.000.000; per tahun Rp12jt; kumulatif 12/24/36/48/60 jt.
  Semua angka turunan = ILUSTRASI (pill ILUSTRASI, BUKAN stempel TERVERIFIKASI).
"""
import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "lifestyle-creep"))

from meja_bedah_v2 import (  # noqa: E402
    AMBER, ARANG, CW, GARIS, H, KERTAS, M, MERAH, TINTA, W,
    arrow_down, center, circle_annotation, fi, fm, fit_inter,
    fit_mono_bold, footer, fmt_idr, hbar, header, new_canvas,
    pill_generic, pill_ilustrasi, right, subhead, text_block, wrap,
)
from render_lifestyle_creep import (  # noqa: E402
    BULAN, KENAIKAN, KUMULATIF, PER_TAHUN, RUBRIK, SETENGAH, TOTAL_5THN,
)

# ------------------------------------------------------------ easing ------
def ease_out_cubic(p):
    return 1.0 - (1.0 - p) ** 3


def ease_out_back(p):
    c1, c3 = 1.70158, 2.70158
    return 1.0 + c3 * (p - 1.0) ** 3 + c1 * (p - 1.0) ** 2


def ease_in_out(p):
    return p * p * (3.0 - 2.0 * p) if p < 0.5 else 1.0 - ((-2.0 * p + 2.0) ** 2) / 2.0


def clamp01(x):
    return 0.0 if x <= 0.0 else (1.0 if x >= 1.0 else x)


# ------------------------------------------------- layer (elemen statis) --
def make_layer(draw_fn, box, pad=8):
    """Gambar elemen ke layer RGBA transparan, crop ke bbox (+pad).

    draw_fn(d): menggambar elemen di koordinat absolut kanvas.
    box: (x0, y0, x1, y1) bbox elemen. Kembalikan (crop_rgba, (x0, y0)).
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_fn(d)
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(W, x1 + pad)
    y1 = min(H, y1 + pad)
    return img.crop((x0, y0, x1, y1)), (x0, y0)


def _paste_alpha(base, crop, x, y, alpha=255):
    """Paste crop RGBA ke base RGB dengan alpha global (0-255)."""
    if alpha <= 0:
        return
    if alpha >= 255:
        mask = crop.split()[3]
    else:
        mask = crop.split()[3].point(lambda v: v * alpha // 255)
    base.paste(crop, (x, y), mask)


def _paste_scaled(base, crop, cx, cy, s, alpha=255):
    """Paste crop di-scale s di sekitar titik tengah (cx, cy).
    Bila s == 1.0, paste langsung tanpa resize (resize LANCZOS di skala 1.0
    menimbulkan noise ±1 di tepi teks — frame akhir harus piksel-identik
    dengan frame statis)."""
    w, h = crop.size
    nw, nh = max(1, round(w * s)), max(1, round(h * s))
    if nw == w and nh == h:
        _paste_alpha(base, crop, round(cx - w / 2), round(cy - h / 2), alpha)
        return
    r = crop.resize((nw, nh), Image.LANCZOS)
    _paste_alpha(base, r, round(cx - nw / 2), round(cy - nh / 2), alpha)


def apply_layer(base, el, t):
    """Terapkan satu elemen layer ke frame base pada waktu t (detik, relatif beat)."""
    p = (t - el["t0"]) / el["dur"]
    if p <= 0:
        return
    p = min(1.0, p)
    mode = el["mode"]
    img, (x0, y0) = el["img"], el["pos"]
    if mode == "pop":
        e = ease_out_back(p)
        s = 0.72 + 0.28 * e
        a = int(255 * min(1.0, p * 2.5))
        _paste_scaled(base, img, el["cx"], el["cy"], s, a)
    elif mode in ("slide_l", "slide_r", "slide_u", "slide_d"):
        e = ease_out_cubic(p)
        a = int(255 * min(1.0, p * 2.5))
        k = 70 * (1.0 - e)
        dx, dy = {"slide_l": (-k, 0), "slide_r": (k, 0),
                  "slide_u": (0, k), "slide_d": (0, -k)}[mode]
        _paste_alpha(base, img, x0 + round(dx), y0 + round(dy), a)
    elif mode == "fade":
        _paste_alpha(base, img, x0, y0, int(255 * p))
    else:
        raise ValueError(f"mode layer tak dikenal: {mode}")


def apply_draw(d, el, t):
    """Terapkan satu elemen dinamis (draw_fn) ke ImageDraw d pada waktu t."""
    p = (t - el["t0"]) / el["dur"]
    if p <= 0:
        return
    p = min(1.0, p)
    e = ease_out_cubic(p) if el.get("ease", True) else p
    el["fn"](d, e, p, t)


# ------------------------------------------------- timing (frasa dari VO) --
def detect_silences(vo_path):
    """Jeda (silence) di file VO via ffmpeg silencedetect. Kembalikan
    list (start, end) dalam detik."""
    cmd = ["ffmpeg", "-v", "info", "-i", str(vo_path),
           "-af", "silencedetect=noise=-40dB:d=0.25", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    sils, cur = [], None
    for line in out.splitlines():
        m1 = re.search(r"silence_start: ([\d.]+)", line)
        m2 = re.search(r"silence_end: ([\d.]+)", line)
        if m1:
            cur = float(m1.group(1))
        if m2 and cur is not None:
            sils.append((cur, float(m2.group(1))))
            cur = None
    return sils


def phrase_starts(segments, sils):
    """Bagi tiap segmen jadi frasa di jeda silence. Kembalikan list per beat:
    list waktu mulai frasa (relatif ke awal beat). Frasa 0 selalu mulai di 0."""
    out = []
    for (a, b) in segments:
        starts = [0.0]
        for (s, e) in sils:
            if s > a + 0.05 and e < b - 0.05:
                starts.append(e - a)
        out.append(starts)
    return out


def at(phrases, idx, seg_dur, default_frac):
    """Waktu mulai frasa idx (relatif beat); fallback ke fraksi segmen bila
    frasa itu tidak ada di VO baru (jumlah frasa berubah)."""
    if 0 <= idx < len(phrases):
        return phrases[idx]
    return seg_dur * default_frac


# ------------------------------------------------------------- helpers ----
def base_canvas(beat):
    """Kanvas + header + footer (chrome statis tiap beat)."""
    img, d = new_canvas()
    header(d, RUBRIK, beat)
    footer(d, beat)
    return img, d


def headline_layer(lines, y0=190, size=88, lh=100):
    """Tiap baris headline jadi elemen layer sendiri (masuk berurutan).

    lines: list (teks, warna). Kembalikan list (layer, box, y).
    """
    els = []
    y = y0
    for text, fill in lines:
        f = fit_inter("ExtraBold", text, size, CW)

        def _draw(d, _t=text, _f=f, _y=y, _c=fill):
            d.text((M, _y), _t, font=_f, fill=_c)

        w = f.getlength(text)
        box = (M, y, M + int(w) + 4, y + size + 8)
        els.append((make_layer(_draw, box), y))
        y += lh
    return els


def subhead_layer(text, y, size=38, fill=ARANG):
    """Subhead (bisa 2 baris) jadi satu elemen layer."""
    f = fi("Regular", size)
    lines = wrap(ImageDraw.Draw(Image.new("RGB", (W, H))), text, f, CW)
    h = len(lines) * (size + 14)

    def _draw(d, _ls=lines, _f=f, _y=y, _c=fill, _s=size):
        for i, ln in enumerate(_ls):
            d.text((M, _y + i * (_s + 14)), ln, font=_f, fill=_c)

    return make_layer(_draw, (M, y, W - M, y + h))


def text_layer(draw_fn, box):
    """Satu elemen layer generik dari draw_fn + bbox."""
    return make_layer(draw_fn, box)


def el_layer(layer, pos, cx, cy, t0, dur, mode):
    return {"kind": "layer", "img": layer[0], "pos": layer[1],
            "cx": cx, "cy": cy, "t0": t0, "dur": dur, "mode": mode}


def el_draw(fn, t0, dur, ease=True):
    return {"kind": "draw", "fn": fn, "t0": t0, "dur": dur, "ease": ease}


# ============================================================ elemen =====
def E(layer, t0, dur, mode):
    """Bungkus layer (crop, pos) jadi elemen animasi."""
    img, (x0, y0) = layer
    w, h = img.size
    return {"kind": "layer", "img": img, "pos": (x0, y0),
            "cx": x0 + w // 2, "cy": y0 + h // 2,
            "t0": t0, "dur": dur, "mode": mode}


def headline_els(lines, t0=0.0, step=0.12, dur=0.35):
    """Baris-baris headline masuk berurutan (slide up)."""
    return [E(layer, t0 + i * step, dur, "slide_u")
            for i, (layer, _y) in enumerate(headline_layer(lines))]


def arc_fn(cx, cy, rx, ry, color=AMBER, width=6):
    """Gambar lingkaran anotasi progresif (sudut -90 -> 270). Di p=1 gambar
    elips penuh (identik dengan circle_annotation statis)."""
    n = 72

    def fn(d, e, p, t):
        if e >= 1.0:
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                      outline=color, width=width)
            return
        k = max(2, int(n * e))
        pts = []
        for i in range(k + 1):
            a = math.radians(-90.0 + 360.0 * i / n)
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        if len(pts) >= 2:
            d.line(pts, fill=color, width=width)

    return fn


def line_draw_fn(points, color, width=6, dot_color=None):
    """Gambar polyline progresif mengikuti panjang kumulatif; di p=1 gambar
    garis penuh joint='curve' (identik statis). Titik vertex muncul saat
    garis melewatinya."""
    segs, total = [], 0.0
    for a, b in zip(points, points[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, ln))
        total += ln
    cum = [0.0]
    for _a, _b, ln in segs:
        cum.append(cum[-1] + ln)

    def fn(d, e, p, t):
        if e >= 1.0:
            d.line(points, fill=color, width=width, joint="curve")
        else:
            dist = e * total
            pts = [points[0]]
            acc = 0.0
            for (a, b, ln) in segs:
                if acc + ln <= dist:
                    pts.append(b)
                    acc += ln
                else:
                    r = (dist - acc) / ln if ln > 0 else 0.0
                    pts.append((a[0] + (b[0] - a[0]) * r,
                                a[1] + (b[1] - a[1]) * r))
                    break
            if len(pts) >= 2:
                d.line(pts, fill=color, width=width)
        for i, pt in enumerate(points):
            frac = cum[i] / total if total > 0 else 0.0
            if e >= frac:
                r = 9
                d.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r],
                          fill=dot_color or color)

    return fn


def count_fn(fmt, target, font, xy, fill, prefix="", suffix=""):
    """Angka menghitung naik 0 -> target (ease-out). fmt: fmt_idr."""
    cx, cy = xy

    def fn(d, e, p, t):
        v = round(target * e)
        text = prefix + fmt(v) + suffix
        w = d.textlength(text, font=font)
        d.text((cx - w / 2, cy), text, font=font, fill=fill)

    return fn


# ============================================================ beat 1 =====
def beat1(P, seg_dur):
    """HOOK: headline -> balok amber tumbuh + count-up -> balok merah -> ringkasan."""
    base, _d = base_canvas(1)
    els = []
    els += headline_els([("GAJI NAIK 2 JUTA,", TINTA),
                         ("TABUNGAN", TINTA),
                         ("TETAP NOL?", AMBER)])
    els.append(E(subhead_layer("Kenapa bisa begitu? Bedah di meja ini.", 502),
                 0.60, 0.35, "fade"))
    # bar 1: label + balok amber tumbuh + angka count-up
    els.append(E(text_layer(
        lambda d: d.text((M, 660), "GAJI NAIK", font=fi("Bold", 40), fill=TINTA),
        (M, 660, M + 300, 660 + 48)), 0.15, 0.30, "pop"))

    def _bar1(d, e, p, t):
        d.rectangle([M, 710, M + 920 * e, 710 + 170], fill=AMBER)

    els.append(el_draw(_bar1, 0.15, 0.65))
    f_num = fit_mono_bold("+Rp2.000.000", 80, W - 2 * M - 60)
    els.append(el_draw(count_fn(fmt_idr, 2_000_000, f_num, (W // 2, 755),
                                KERTAS, prefix="+"), 0.20, 0.70))
    els.append(E(text_layer(
        lambda d: center(d, W // 2, 920, "LARINYA KE MANA?", fm(True, 30), ARANG),
        (M, 920, W - M, 920 + 36)), 1.00, 0.30, "fade"))
    # bar 2: label + outline tumbuh + Rp0 + lingkaran
    els.append(E(text_layer(
        lambda d: d.text((M, 990), "TABUNGAN", font=fi("Bold", 40), fill=TINTA),
        (M, 990, M + 300, 990 + 48)), at(P, 1, seg_dur, 0.44), 0.30, "pop"))

    def _bar2(d, e, p, t):
        d.rectangle([M, 1040, M + 920 * e, 1040 + 170],
                    outline=MERAH, width=5)

    els.append(el_draw(_bar2, at(P, 1, seg_dur, 0.44), 0.50))
    f0 = fit_mono_bold("Rp0", 120, W - 2 * M - 60)
    els.append(E(text_layer(
        lambda d: center(d, W // 2, 1065, "Rp0", f0, MERAH),
        (M, 1040, W - M, 1040 + 170)), at(P, 1, seg_dur, 0.44) + 0.35, 0.35, "pop"))
    els.append(el_draw(arc_fn(W // 2, 1125, 240, 105),
                       at(P, 1, seg_dur, 0.44) + 0.55, 0.45))
    # ringkasan + pill
    els.append(E(text_layer(
        lambda d: _summary(d, 1400, "GAJI NAIK 2 JUTA — TABUNGAN NOL"),
        (M, 1400, W - M, 1400 + 118)), at(P, 2, seg_dur, 0.81), 0.30, "slide_u"))
    els.append(E(text_layer(
        lambda d: pill_ilustrasi(d, M, 1544, "Angka hook — contoh, bukan survei."),
        (M, 1544, W - M, 1544 + 56)), at(P, 2, seg_dur, 0.81) + 0.25, 0.30, "fade"))
    return base, els


def _summary(d, y, text, size=52):
    """Isi summary_rule tanpa return (untuk layer)."""
    d.line([(M, y), (W - M, y)], fill=TINTA, width=3)
    f = fit_mono_bold(text, size, CW)
    d.text((M, y + 18), text, font=f, fill=TINTA)
    d.line([(M, y + 92), (W - M, y + 92)], fill=TINTA, width=3)


# ============================================================ beat 2 =====
def beat2(P, seg_dur):
    """3 jalur bocor muncul satu per satu mengikuti VO, lalu ledger terisi."""
    base, _d = base_canvas(2)
    els = []
    els += headline_els([("GAJI NAIK,", TINTA),
                         ("GAYA HIDUP", TINTA),
                         ("NAIK DULUAN.", AMBER)])
    els.append(E(subhead_layer(
        "Kopi naik kelas, langganan nambah, cicilan baru muncul.", 502),
        0.60, 0.35, "fade"))
    rows = [("KOPI", "naik kelas"), ("LANGGANAN", "nambah terus"),
            ("CICILAN", "baru muncul")]
    # Jangkar frasa: headline bisa 1 frasa (Senandika brisk) atau 2 frasa
    # (Deden lambat). h = indeks frasa pertama setelah headline (~25% beat).
    # Tiga jalur bocor = 3 frasa setelah headline; ledger = frasa berikutnya.
    # Bila frasa terlalu sedikit (storytelling 3 frasa — ketiga jalur disebut
    # dalam 1 frasa), sebar baris di jendela sebelum ledger.
    h = next((i for i, p in enumerate(P) if p >= 0.25 * seg_dur), len(P) - 1)
    if len(P) >= h + 4:
        row_times = [P[h + k] for k in range(3)]
        led_t = P[h + 3]
    else:
        led_t = P[-1]
        row_times = [led_t - 2.25 + k * 0.65 for k in range(3)]
    for k, (label, sub) in enumerate(rows):
        ry = 690 + k * 180
        t0 = row_times[k]
        cx = W - M - 40

        def _bar(d, e, p, t, _ry=ry):
            d.rectangle([M, _ry, M + 14, _ry + 110 * e], fill=MERAH)

        els.append(el_draw(_bar, t0, 0.30))

        def _txt(d, _l=label, _s=sub, _ry=ry):
            d.text((M + 34, _ry - 6), _l, font=fi("Bold", 42), fill=TINTA)
            d.text((M + 34, _ry + 48), _s, font=fi("Regular", 32), fill=ARANG)

        els.append(E(text_layer(_txt, (M + 34, ry - 6, W - M, ry + 110)),
                     t0 + 0.08, 0.30, "slide_l"))

        def _tri(d, _cx=cx, _ry=ry):
            d.polygon([(_cx - 26, _ry + 8), (_cx + 26, _ry + 8),
                       (_cx, _ry + 56)], fill=MERAH)

        els.append(E(text_layer(_tri, (cx - 30, ry, cx + 30, ry + 60)),
                     t0 + 0.18, 0.25, "pop"))
    # ledger: kotak dulu, lalu baris terisi satu per satu
    t_led = led_t

    def _box(d):
        d.rectangle([M, 1260, W - M, 1260 + 218], outline=TINTA, width=3)
        d.line([(M, 1260 + 218 - 8), (W - M, 1260 + 218 - 8)], fill=TINTA, width=3)

    els.append(E(text_layer(_box, (M, 1260, W - M, 1260 + 218)),
                 t_led, 0.35, "fade"))
    led_rows = [("MASUK    +Rp2.000.000", TINTA),
                ("KELUAR   -Rp2.000.000", MERAH),
                ("SISA     Rp0", MERAH)]
    for i, (text, fill) in enumerate(led_rows):
        f = fit_mono_bold(text, 44, CW - 40)

        def _row(d, _t=text, _f=f, _c=fill, _i=i):
            d.text((M + 20, 1260 + 18 + _i * 62), _t, font=_f, fill=_c)

        els.append(E(text_layer(_row, (M, 1260 + 18 + i * 62,
                                       W - M, 1260 + 18 + i * 62 + 50)),
                     t_led + 0.15 + i * 0.45, 0.30, "slide_l"))
    els.append(E(text_layer(
        lambda d: pill_ilustrasi(
            d, M, 1560, "Kenaikan habis tanpa jejak — contoh dari hook."),
        (M, 1560, W - M, 1560 + 56)),
        max(t_led + 1.75, at(P, h + 4, seg_dur, 0.85)), 0.30, "fade"))
    return base, els


# ============================================================ beat 3 =====
def beat3(P, seg_dur):
    """Definisi: dua garis digambar progresif, pengeluaran lebih curam."""
    base, _d = base_canvas(3)
    els = []
    els += headline_els([("LIFESTYLE", TINTA), ("CREEP", AMBER)])
    els.append(E(subhead_layer(
        "Pengeluaran naik secepat penghasilan — bahkan lebih cepat.", 402),
        0.55, 0.35, "fade"))

    def _legend(d):
        ly = 620
        d.line([(M, ly + 14), (M + 60, ly + 14)], fill=TINTA, width=6)
        d.ellipse([M + 24, ly + 8, M + 36, ly + 20], fill=AMBER)
        d.text((M + 76, ly), "PENGHASILAN", font=fm(True, 30), fill=TINTA)
        d.line([(M + 400, ly + 14), (M + 460, ly + 14)], fill=MERAH, width=6)
        d.ellipse([M + 424, ly + 8, M + 436, ly + 20], fill=MERAH)
        d.text((M + 476, ly), "PENGELUARAN", font=fm(True, 30), fill=MERAH)

    els.append(E(text_layer(_legend, (M, 620, W - M, 620 + 40)),
                 0.75, 0.35, "fade"))

    def _axis(d, e, p, t):
        d.line([(M, 1330), (M + 920 * e, 1330)], fill=TINTA, width=3)

    els.append(el_draw(_axis, 1.00, 0.30))
    gaji = [(160, 1230), (360, 1180), (560, 1120), (760, 1050), (960, 980)]
    keluar = [(160, 1230), (360, 1140), (560, 1030), (760, 880), (960, 700)]
    els.append(el_draw(line_draw_fn(gaji, TINTA, 6, dot_color=AMBER),
                       # Garis = isi frasa pertama (definisi). JANGAN diikat ke
                       # awal frasa 1: pada VO storytelling frasa 0 panjang
                       # (Senandika: 0-4,62 dtk) dan frasa 1 = kalimat penutup.
                       # 0,35*seg = setelah headline + legenda + sumbu.
                       0.35 * seg_dur, 1.55))
    els.append(el_draw(line_draw_fn(keluar, MERAH, 6, dot_color=MERAH),
                       0.35 * seg_dur + 0.27, 1.45))
    els.append(el_draw(arc_fn(960, 700, 100, 66),
                       # Lingkaran di ujung garis merah, di kalimat penutup
                       # (~80% beat — cocok dgn frasa terakhir di kedua VO).
                       0.80 * seg_dur, 0.40))
    els.append(E(text_layer(
        lambda d: right(d, W - M, 1354, "WAKTU →", fm(False, 28), ARANG),
        (W - M - 220, 1354, W - M, 1354 + 28)), 0.80 * seg_dur + 0.30,
        0.25, "fade"))
    els.append(E(subhead_layer(
        "Standar ‘kebutuhan’ ikut bergeser tiap gaji naik.", 1460, size=34),
        0.80 * seg_dur + 0.40, 0.30, "fade"))
    return base, els


# ============================================================ beat 4 =====
def beat4(P, seg_dur):
    """Aturan setengah: balok tumbuh utuh, lalu TERBELAH 50/50 (wipe)."""
    base, _d = base_canvas(4)
    els = []
    els += headline_els([("ATURAN SETENGAH", TINTA), ("KENAIKAN", TINTA)])
    els.append(E(subhead_layer(
        "Setengah kenaikan langsung pindah ke tabungan — otomatis di hari gajian.",
        402), 0.55, 0.35, "fade"))
    by, bh = 680, 180
    half = (W - 2 * M) // 2
    # Jangkar turunan: balok tumbuh di awal beat (JANGAN di awal frasa 1 —
    # pada VO storytelling frasa 0 panjang, frasa 1 bisa di 79% beat);
    # belah setelah balok penuh; stempel di frasa terakhir
    # ("otomatis di hari gajian" = ekor kalimat solusi).
    bar_t = max(0.65, min(at(P, 1, seg_dur, 0.14), 0.25 * seg_dur))
    wipe_t = max(at(P, 2, seg_dur, 0.37), bar_t + 1.0)
    ledger_t = max(at(P, 3, seg_dur, 0.50), wipe_t + 0.9)
    stamp_t = max(at(P, len(P) - 1, seg_dur, 0.68), ledger_t + 1.2)

    def _bar(d, e, p, t):
        d.rectangle([M, by, M + 920 * e, by + bh], fill=AMBER)

    els.append(el_draw(_bar, bar_t, 0.70))
    f50 = fit_mono_bold("50%", 72, half - 40)
    els.append(E(text_layer(
        lambda d: center(d, M + half // 2, by + 54, "50%", f50, KERTAS),
        (M, by, M + half, by + bh)),
        bar_t + 0.68, 0.30, "pop"))

    def _wipe(d, e, p, t):
        x0 = M + half
        w = half * e
        if w > 0:
            d.rectangle([x0, by, x0 + w, by + bh], fill=KERTAS)
            # Kertas polos menutupi garis buku (rule) kanvas — gambar ulang
            # garis yang memotong area wipe supaya sama dengan statis.
            for ry in range(96, H, 96):
                if by <= ry <= by + bh:
                    d.line([(x0, ry), (x0 + w, ry)], fill=GARIS, width=2)
        if e > 0.15:
            # Garis pembagi tumbuh dari atas. x0+1 supaya band 4px-nya
            # (540-543) sama dengan tepi kiri outline rect statis
            # (PIL: outline di dalam, line terpusat — x0 saja = 539-542).
            y1 = by + bh * min(1.0, (e - 0.15) / 0.5)
            d.line([(x0 + 1, by), (x0 + 1, y1)], fill=TINTA, width=4)
        if e > 0.60:
            d.rectangle([x0, by, x0 + half, by + bh], outline=TINTA, width=4)

    els.append(el_draw(_wipe, wipe_t, 0.50))
    els.append(E(text_layer(
        lambda d: center(d, M + half + half // 2, by + 54, "50%", f50, TINTA),
        (M + half, by, M + 920, by + bh)),
        wipe_t + 0.32, 0.30, "pop"))
    els.append(E(text_layer(
        lambda d: (
            center(d, M + half // 2, by + bh + 22, "TABUNGAN OTOMATIS",
                   fi("Bold", 34), TINTA),
            center(d, M + half + half // 2, by + bh + 22, "BOLEH DINIKMATI",
                   fi("Bold", 34), TINTA)),
        (M, by + bh + 22, W - M, by + bh + 62)),
        wipe_t + 0.65, 0.30, "slide_u"))
    els.append(E(text_layer(
        lambda d: _ledger1(d, 990, ["Rp2.000.000 ÷ 2 = Rp1.000.000 / bln"]),
        (M, 990, W - M, 990 + 94)), ledger_t, 0.35, "slide_u"))
    els.append(E(text_layer(
        lambda d: _stamp(d),
        (M, 1180, W - M, 1180 + 110)), stamp_t, 0.30, "pop"))
    els.append(E(text_layer(
        lambda d: _summary(d, 1400, "SETENGAH DITABUNG — SETENGAH DINIKMATI"),
        (M, 1400, W - M, 1400 + 118)), stamp_t + 0.75, 0.30,
        "slide_u"))
    els.append(E(text_layer(
        lambda d: pill_ilustrasi(d, M, 1560, "50% dari panduan; angka rupiah contoh hook."),
        (M, 1560, W - M, 1560 + 56)), stamp_t + 1.05, 0.30, "fade"))
    return base, els


def _ledger1(d, y, lines, size=44):
    h = 18 + len(lines) * 62 + 14
    d.rectangle([M, y, W - M, y + h], outline=TINTA, width=3)
    for i, ln in enumerate(lines):
        f = fit_mono_bold(ln, size, CW - 40)
        d.text((M + 20, y + 18 + i * 62), ln, font=f, fill=TINTA)
    d.line([(M, y + h - 8), (W - M, y + h - 8)], fill=TINTA, width=3)


def _stamp(d):
    sy = 1180
    d.rectangle([M, sy, W - M, sy + 110], fill=TINTA)
    center(d, W // 2, sy + 30, "OTOMATIS DI HARI GAJIAN", fi("Bold", 44), KERTAS)


def arrow_down_fn(cx, y0, y1, fill=TINTA, w=5, head=22):
    """Panah bawah digambar progresif (garis tumbuh + titik berjalan);
    di p=1 identik dengan arrow_down statis."""
    def fn(d, e, p, t):
        if e >= 1.0:
            arrow_down(d, cx, y0, y1, fill=fill, w=w, head=head)
            return
        y = y0 + (y1 - head - y0) * e
        if y > y0:
            d.line([(cx, y0), (cx, y)], fill=fill, width=w)
        r = 7
        d.ellipse([cx - r, y - r, cx + r, y + r], fill=fill)

    return fn


def arrow_right_fn(x0, x1, cy, fill=TINTA, w=5, head=20):
    """Panah kanan progresif; di p=1 = garis + kepala (beat 6)."""
    def fn(d, e, p, t):
        if e >= 1.0:
            d.line([(x0, cy), (x1, cy)], fill=fill, width=w)
            d.polygon([(x1, cy - head), (x1, cy + head), (x1 + 22, cy)],
                      fill=fill)
            return
        x = x0 + (x1 - x0) * e
        if x > x0:
            d.line([(x0, cy), (x, cy)], fill=fill, width=w)
        r = 7
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=fill)

    return fn


def count_fn_right(fmt, target, font, x_right, y, fill, prefix=""):
    """Count-up rata kanan (kolom angka beat 6)."""
    def fn(d, e, p, t):
        v = round(target * e)
        text = prefix + fmt(v)
        w = d.textlength(text, font=font)
        d.text((x_right - w, y), text, font=font, fill=fill)

    return fn


def typewriter_fn(text, font, xy, fill):
    """Teks mengetik + kursor amber; di p=1 = teks penuh + kursor statis."""
    def fn(d, e, p, t):
        k = int(round(len(text) * e))
        shown = text[:k]
        d.text(xy, shown, font=font, fill=fill)
        if shown:
            cx = xy[0] + d.textlength(shown, font=font) + 14
            d.rectangle([cx, xy[1] + 6, cx + 6, xy[1] + 46], fill=AMBER)

    return fn


# ============================================================ beat 5 =====
def beat5(P, seg_dur):
    """Bayar diri sendiri dulu: 3 kotak berurutan, panah mengalir turun."""
    base, _d = base_canvas(5)
    els = []
    els += headline_els([("BAYAR DIRI", TINTA), ("SENDIRI DULU", AMBER)])
    els.append(E(subhead_layer(
        "Baru sisanya untuk hidup — supaya tidak merasa tersiksa.", 402),
        0.55, 0.35, "fade"))
    # kotak 1: GAJIAN
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([M, 620, W - M, 620 + 190], outline=TINTA, width=4),
            center(d, W // 2, 648, "GAJIAN", fi("Bold", 40), TINTA),
            center(d, W // 2, 708, "Rp2.000.000",
                   fit_mono_bold("Rp2.000.000", 60, W - 2 * M - 60), TINTA)),
        (M, 620, W - M, 620 + 190)), 0.0, 0.35, "pop"))
    els.append(el_draw(arrow_down_fn(W // 2, 818, 868), 0.45, 0.40))
    # kotak 2: TABUNGAN DULU (amber) — muncul di tengah frasa "bayar diri
    # sendiri dulu" (bukan di awal frasa berikutnya; frasa itu sendiri yang
    # menyebut aksinya).
    box2_t = 0.5 * at(P, 1, seg_dur, 0.25)
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([M, 876, W - M, 876 + 240], fill=AMBER),
            center(d, W // 2, 906, "TABUNGAN DULU", fi("Bold", 44), KERTAS),
            center(d, W // 2, 970, "Rp1.000.000",
                   fit_mono_bold("Rp1.000.000", 64, W - 2 * M - 60), KERTAS),
            center(d, W // 2, 1060, "otomatis", fi("Regular", 30), KERTAS)),
        (M, 876, W - M, 876 + 240)), box2_t, 0.35, "pop"))
    els.append(el_draw(arrow_down_fn(W // 2, 1124, 1174),
                       box2_t + 0.45, 0.40))
    # kotak 3: SISANYA UNTUK HIDUP
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([M, 1182, W - M, 1182 + 220], outline=TINTA, width=4),
            center(d, W // 2, 1210, "SISANYA UNTUK HIDUP", fi("Bold", 40), TINTA),
            center(d, W // 2, 1270, "Rp1.000.000",
                   fit_mono_bold("Rp1.000.000", 60, W - 2 * M - 60), TINTA),
            center(d, W // 2, 1350, "boleh dinikmati", fi("Regular", 30), ARANG)),
        (M, 1182, W - M, 1182 + 220)),
        box2_t + 0.90, 0.35, "pop"))
    els.append(E(text_layer(
        lambda d: pill_ilustrasi(d, M, 1490, "Setengah kenaikan = Rp1.000.000/bln."),
        (M, 1490, W - M, 1490 + 56)), at(P, 2, seg_dur, 0.48), 0.30, "fade"))
    return base, els


# ============================================================ beat 6 =====
def beat6(P, seg_dur):
    """Simulasi 60 juta: ledger terisi -> kolom kanan menumpuk -> kolom kiri
    kosong -> panah -> ringkasan. Geometri = sampel ACC (1:1)."""
    base, _d = base_canvas(6)
    els = []
    els += headline_els([("KENAIKAN 2 JUTA,", TINTA),
                         ("SETENGAHNYA", TINTA),
                         ("JADI 60 JUTA.", AMBER)])
    els.append(E(subhead_layer(
        "Aturan setengah kenaikan — tabung otomatis di hari gajian.", 502,
        size=36), 0.55, 0.35, "fade"))
    # ledger: kotak dulu, baris terisi satu per satu
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([M, 564, W - M, 564 + 150], outline=TINTA, width=3),
            d.line([(M, 564 + 150 - 8), (W - M, 564 + 150 - 8)], fill=TINTA,
                   width=3)),
        (M, 564, W - M, 564 + 150)), 0.0, 0.35, "fade"))
    led = ["Rp2.000.000 ÷ 2 = Rp1.000.000 / bln",
           "Rp1.000.000 × 60 bln = Rp60.000.000"]
    # --- jangkar turunan (bukan waktu absolut): urutan elemen mengikuti
    # frasa VO, bukan jam Deden. Pada VO storytelling frasa 0 panjang dan
    # memuat SELURUH hitungan ledger ("Kenaikan 2 juta, setengahnya 1 juta
    # ditabung...") — kedua baris ledger muncul DI DALAM frasa 0 (30% dan
    # 65%-nya), kolom kanan di frasa 1 ("Lima tahun, itu jadi 60 juta"),
    # kolom kiri di frasa 3 ("Tanpa aturan ini").
    row1_t = max(0.65, 0.30 * at(P, 1, seg_dur, 0.10))
    row2_t = max(row1_t + 0.8, 0.65 * at(P, 1, seg_dur, 0.20))
    right_t = min(at(P, 1, seg_dur, 0.43) + 0.3, seg_dur - 6.0)
    count_t = right_t + 0.1
    left_t = max(at(P, 3, seg_dur, 0.74), count_t + 3.3)
    left_t = min(left_t, seg_dur - 3.4)  # sisakan ruang panah+ringkasan+pill
    arrow_t = left_t + 2.2
    for i, ln in enumerate(led):
        f = fit_mono_bold(ln, 44, W - 2 * M - 40)

        def _row(d, _t=ln, _f=f, _i=i):
            d.text((M + 20, 564 + 18 + _i * 62), _t, font=_f, fill=TINTA)

        els.append(E(text_layer(_row, (M, 564 + 18 + i * 62,
                                       W - M, 564 + 18 + i * 62 + 50)),
                     (row1_t, row2_t)[i], 0.30, "slide_l"))
    # kolom kanan: ATURAN SETENGAH
    rx, col_w, col_y0, col_y1 = W - M - 440, 440, 758, 758 + 640
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([rx, col_y0, rx + col_w, col_y1], outline=TINTA, width=4),
            d.rectangle([rx, col_y0, rx + col_w, col_y0 + 72], fill=TINTA),
            center(d, rx + col_w / 2, col_y0 + 16, "ATURAN SETENGAH",
                   fi("Bold", 34), KERTAS)),
        (rx, col_y0, rx + col_w, col_y1)), right_t, 0.35, "fade"))
    f60 = fit_mono_bold("Rp60.000.000", 46, col_w - 60)
    els.append(el_draw(count_fn(fmt_idr, 60_000_000, f60, (rx + col_w / 2, col_y0 + 104),
                                TINTA), count_t, 2.50))
    els.append(E(text_layer(
        lambda d: center(d, rx + col_w / 2, col_y0 + 168, "dalam 5 tahun",
                         fi("Regular", 34), ARANG),
        (rx, col_y0 + 168, rx + col_w, col_y0 + 168 + 40)),
        count_t + 2.10, 0.30, "fade"))
    cum = [12, 24, 36, 48, 60]
    for i in range(5):
        by = col_y0 + 232 + i * 56
        t0 = count_t + 0.32 + 0.50 * i

        def _bar(d, e, p, t, _by=by):
            d.rectangle([rx + 40, _by, rx + 40 + 290 * e, _by + 40], fill=AMBER)

        els.append(el_draw(_bar, t0, 0.45))
        els.append(E(text_layer(
            lambda d, _by=by, _i=i: (
                d.text((rx + 56, _by + 8), f"Thn {_i + 1}  +Rp12 jt",
                       font=fi("Bold", 24), fill=TINTA)),
            (rx + 40, by, rx + col_w - 110, by + 40)), t0 + 0.35, 0.20, "fade"))
        els.append(E(text_layer(
            lambda d, _by=by, _i=i: (
                d.text((rx + col_w - 96, _by + 6), f"{cum[_i]} jt",
                       font=fm(True, 26), fill=TINTA)),
            (rx + col_w - 110, by, rx + col_w, by + 40)), t0 + 0.35, 0.20, "fade"))
    els.append(el_draw(arc_fn(rx + col_w / 2, col_y0 + 130, 195, 30),
                       count_t + 2.60, 0.40))
    # kolom kiri: TANPA ATURAN
    lx = M
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([lx, col_y0, lx + col_w, col_y1], outline=MERAH, width=4),
            d.rectangle([lx, col_y0, lx + col_w, col_y0 + 72], fill=MERAH),
            center(d, lx + col_w / 2, col_y0 + 16, "TANPA ATURAN",
                   fi("Bold", 34), KERTAS)),
        (lx, col_y0, lx + col_w, col_y1)), left_t, 0.35, "fade"))
    f0 = fit_mono_bold("Rp0", 120, col_w - 40)
    els.append(E(text_layer(
        lambda d: center(d, lx + col_w / 2, col_y0 + 110, "Rp0", f0, MERAH),
        # kotak 140 tinggi (bukan 120): descender "p" di 120px turun s.d. ~136px
        (lx, col_y0 + 110, lx + col_w, col_y0 + 110 + 140)),
        left_t + 0.35, 0.30, "pop"))
    els.append(E(text_layer(
        lambda d: (
            center(d, lx + col_w / 2, col_y0 + 250, "kenaikan habis",
                   fi("Regular", 34), ARANG),
            center(d, lx + col_w / 2, col_y0 + 292, "jadi nol",
                   fi("Regular", 34), ARANG)),
        (lx, col_y0 + 250, lx + col_w, col_y0 + 292 + 40)),
        left_t + 0.65, 0.30, "fade"))
    for i in range(5):
        by = col_y0 + 360 + i * 48

        def _empty(d, _by=by, _i=i):
            d.rectangle([lx + 40, _by, lx + col_w - 40, _by + 30],
                        outline=MERAH, width=2)
            d.text((lx + 56, _by + 2), f"Thn {_i + 1}", font=fm(False, 22),
                   fill=MERAH)
            d.text((lx + col_w - 130, _by + 2), "Rp0", font=fm(True, 22),
                   fill=MERAH)

        els.append(E(text_layer(_empty, (lx + 40, by, lx + col_w - 40, by + 30)),
                     left_t + 0.95 + i * 0.18, 0.25, "fade"))
    # panah antar kolom
    els.append(el_draw(arrow_right_fn(lx + col_w + 8, rx - 8, col_y0 + 320),
                       arrow_t, 0.35))
    # ringkasan + pill
    els.append(E(text_layer(
        lambda d: _summary(d, 1442, "SELISIH: Rp60.000.000"),
        (M, 1442, W - M, 1442 + 118)), arrow_t + 0.35, 0.30, "slide_u"))
    els.append(E(text_layer(
        lambda d: pill_ilustrasi(d, M, 1560, "Simulasi dari angka hook; tanpa imbal hasil."),
        (M, 1560, W - M, 1560 + 56)), arrow_t + 0.85, 0.30, "fade"))
    return base, els


# ============================================================ beat 7 =====
def beat7(P, seg_dur):
    """Affiliate: kartu buku slide masuk, kolom etalase menyusul."""
    base, _d = base_canvas(7)
    els = []
    els += headline_els([("BACAAN LANJUTAN:", TINTA), ("ATOMIC HABITS", AMBER)])
    els.append(E(subhead_layer(
        "Buku Atomic Habits bisa jadi bacaan lanjutannya.", 402),
        0.55, 0.35, "fade"))
    bx, by, bw, bh = M, 700, 400, 720
    # kerangka kartu
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([bx, by, bx + bw, by + bh], outline=TINTA, width=4),
            d.rectangle([bx, by, bx + bw, by + 16], fill=TINTA)),
        (bx, by, bx + bw, by + bh)), 0.0, 0.40, "slide_l"))
    els.append(E(text_layer(
        lambda d: center(d, bx + bw / 2, by + 200, "ATOMIC",
                         fit_inter("ExtraBold", "ATOMIC", 64, bw - 60), TINTA),
        (bx, by + 200, bx + bw, by + 200 + 64)), 0.25, 0.30, "pop"))
    els.append(E(text_layer(
        lambda d: center(d, bx + bw / 2, by + 280, "HABITS",
                         fit_inter("ExtraBold", "HABITS", 64, bw - 60), TINTA),
        (bx, by + 280, bx + bw, by + 280 + 64)), 0.45, 0.30, "pop"))

    def _rule(d, e, p, t):
        d.line([(bx + 60, by + 380), (bx + 60 + 280 * e, by + 380)],
               fill=AMBER, width=6)

    els.append(el_draw(_rule, 0.70, 0.25))
    els.append(E(text_layer(
        lambda d: center(d, bx + bw / 2, by + 420, "JAMES CLEAR",
                         fm(True, 30), TINTA),
        (bx, by + 420, bx + bw, by + 420 + 30)), 0.85, 0.25, "fade"))
    els.append(E(text_layer(
        lambda d: center(d, bx + bw / 2, by + 470, "BUKU", fm(False, 28), ARANG),
        (bx, by + 470, bx + bw, by + 470 + 28)), 1.00, 0.25, "fade"))
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([bx + bw - 70, by + 16, bx + bw - 26, by + 130], fill=AMBER),
            d.polygon([(bx + bw - 70, by + 130), (bx + bw - 26, by + 130),
                       (bx + bw - 48, by + 104)], fill=KERTAS)),
        (bx + bw - 70, by + 16, bx + bw - 26, by + 130)), 1.20, 0.30, "slide_d"))
    # kolom kanan
    rx, col_w = M + bw + 60, W - M - (M + bw + 60)
    col_t = at(P, 1, seg_dur, 0.32)
    els.append(E(text_layer(
        lambda d: d.text((rx, 720), "CEK ETALASE", font=fi("Bold", 44), fill=TINTA),
        (rx, 720, W - M, 720 + 44)), col_t, 0.30, "slide_r"))
    els.append(E(text_layer(
        lambda d: d.text((rx, 786), "LINK BIO",
                         font=fit_mono_bold("LINK BIO", 72, col_w), fill=TINTA),
        (rx, 786, W - M, 786 + 72)), col_t + 0.25, 0.30, "slide_r"))

    def _rline(d, e, p, t):
        d.line([(rx, 900), (rx + (W - M - rx) * e, 900)], fill=TINTA, width=3)

    els.append(el_draw(_rline, col_t + 0.55, 0.25))
    els.append(E(text_layer(
        lambda d: pill_generic(d, rx, 940, "LINK MENYUSUL", outline=AMBER,
                               text_fill=AMBER),
        (rx, 940, W - M, 940 + 56)), col_t + 0.85, 0.25, "pop"))
    els.append(E(text_layer(
        lambda d: _text_block(d, rx, 1040,
                              "Link affiliate menyusul — cek etalase di link bio.",
                              32, col_w),
        (rx, 1040, W - M, 1040 + 92)), col_t + 1.10, 0.30, "fade"))
    # "Kenapa nyambung?" + penjelasan SETELAH blok etalase selesai —
    # JANGAN diikat ke frasa (pada VO dgn frasa sedikit, fallback-nya bisa
    # jatuh SEBELUM pill, membalik urutan baca atas-bawah).
    els.append(E(text_layer(
        lambda d: d.text((rx, 1200), "Kenapa nyambung?", font=fi("Bold", 32),
                         fill=TINTA),
        (rx, 1200, W - M, 1200 + 32)), col_t + 1.35, 0.25, "fade"))
    els.append(E(text_layer(
        lambda d: _text_block(d, rx, 1244,
                              "Kebiasaan otomatis = inti solusi video ini.",
                              32, col_w),
        (rx, 1244, W - M, 1244 + 92)), col_t + 1.60, 0.30, "fade"))
    els.append(E(text_layer(
        lambda d: center(d, W // 2, 1520, "ATOMIC HABITS — JAMES CLEAR",
                         fit_mono_bold("ATOMIC HABITS — JAMES CLEAR", 36, CW), TINTA),
        (M, 1520, W - M, 1520 + 36)), 0.92 * seg_dur, 0.30, "fade"))
    return base, els


def _text_block(d, x, y, text, size, max_w):
    for ln in wrap(d, text, fi("Regular", size), max_w):
        d.text((x, y), ln, font=fi("Regular", size), fill=ARANG)
        y += size + 14


# ============================================================ beat 8 =====
def beat8(P, seg_dur):
    """CTA komen: dua pilihan pop, kotak komentar mengetik, ajakan share."""
    base, _d = base_canvas(8)
    els = []
    els += headline_els([("KENAIKAN GAJI", TINTA),
                         ("TERAKHIRMU", TINTA),
                         ("LARINYA KE MANA?", AMBER)])
    els.append(E(subhead_layer("Tulis di komen — tabungan atau gaya hidup?", 502),
                 0.55, 0.35, "fade"))
    by, bh, bw = 680, 300, 440
    lx, rx = M, W - M - bw
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([lx, by, lx + bw, by + bh], fill=AMBER),
            center(d, lx + bw / 2, by + 90, "TABUNGAN",
                   fit_mono_bold("TABUNGAN", 54, bw - 40), KERTAS),
            center(d, lx + bw / 2, by + 170, "disimpan dulu",
                   fi("Regular", 30), KERTAS)),
        (lx, by, lx + bw, by + bh)), 0.30, 0.35, "pop"))
    els.append(E(text_layer(
        lambda d: (
            d.rectangle([rx, by, rx + bw, by + bh], outline=TINTA, width=4),
            center(d, rx + bw / 2, by + 90, "GAYA HIDUP",
                   fit_mono_bold("GAYA HIDUP", 48, bw - 40), TINTA),
            center(d, rx + bw / 2, by + 170, "dinikmati dulu",
                   fi("Regular", 30), ARANG)),
        (rx, by, rx + bw, by + bh)), 0.80, 0.35, "pop"))
    # kotak komentar: outline fade, teks mengetik. Waktu FIX (bukan frasa):
    # pada VO storytelling frasa 1 bisa sangat lambat (Senandika speed 100:
    # 4,39 dtk) sementara pill/share diikat fraksi — mengikat kotak ke frasa
    # akan membalik urutan (pill muncul SEBELUM kotaknya). Kotak muncul
    # tepat setelah kedua kotak pilihan (0,30/0,80), saat VO mengucap
    # "Tulis di komen".
    els.append(E(text_layer(
        lambda d: d.rectangle([M, 1080, W - M, 1080 + 170], outline=TINTA, width=3),
        (M, 1080, W - M, 1080 + 170)), 0.90, 0.30, "fade"))
    els.append(el_draw(typewriter_fn("Tulis di komen...", fi("Regular", 40),
                                     (M + 28, 1080 + 56), ARANG),
                       1.15, 1.30))
    els.append(E(text_layer(
        lambda d: pill_generic(d, M, 1340, "TULIS DI KOMEN", fill=TINTA,
                               text_fill=KERTAS),
        (M, 1340, W - M, 1340 + 56)), 3.20, 0.30, "pop"))
    els.append(E(text_layer(
        lambda d: (
            center(d, W // 2, 1470, "Share ke teman yang gajinya naik,",
                   fi("Regular", 34), ARANG),
            center(d, W // 2, 1514, "tabungannya tetap nol.",
                   fi("Regular", 34), ARANG)),
        (M, 1470, W - M, 1470 + 78)), 0.64 * seg_dur, 0.30, "fade"))
    return base, els


# ============================================================ render ======
def load_segments(path):
    """Baca vo_segments.json -> list {'start': float, 'end': float} per beat.
    Format file: {"segments": [[start, end], ...]} (8 pasang, berurutan)."""
    data = json.loads(Path(path).read_text())
    segs = data["segments"]
    out = []
    for s in segs:
        a, b = float(s[0]), float(s[1])
        out.append({"start": a, "end": b})
    assert len(out) == 8, f"harus 8 segmen, dapat {len(out)}"
    return out


BUILDERS = {1: beat1, 2: beat2, 3: beat3, 4: beat4,
            5: beat5, 6: beat6, 7: beat7, 8: beat8}

# Gaya transisi antar beat (xfade ffmpeg), urutan batas 1->2 ... 7->8.
TRANSITIONS = ["slideleft", "slideup", "wipeleft", "slidedown",
               "slideleft", "fade", "slideup"]


def phrase_starts_from(silences, start, end):
    """Seperti phrase_starts tapi dari daftar jeda yang sudah dideteksi
    (dipakai main() supaya silencedetect hanya jalan sekali)."""
    dur = end - start
    bounds = [start]
    for s, e in silences:
        mid = (s + e) / 2.0
        if start + 0.3 < mid < end - 0.3 and mid - bounds[-1] > 0.25:
            bounds.append(mid)
    bounds.append(end)
    n = len(bounds) - 1
    if n > 8:
        bounds = [bounds[0]] + bounds[1:][:: max(1, (n - 1) // 7)][:7] + [end]
    # Kembalikan DETIK absolut relatif awal beat (bukan fraksi) — konsisten
    # dengan phrase_starts() dan at() (fallback = seg_dur * fraksi).
    return [(b - start) for b in bounds[:-1]], n


def render_beat(beat, P, seg_dur, out_dir, fps=30, tail=0.45):
    """Render semua frame satu beat ke out_dir/%04d.png.
    tail: ekor hold (frame final ditahan) untuk jendela xfade; beat 8 = 0."""
    base, els = BUILDERS[beat](P, seg_dur)
    dur = seg_dur + (tail if beat < 8 else 0.0)
    n = int(round(dur * fps))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        t = i / fps
        frame = base.copy()
        d = ImageDraw.Draw(frame)
        for el in els:
            if el["kind"] == "layer":
                apply_layer(frame, el, t)
            else:
                apply_draw(d, el, t)
        frame.save(out_dir / f"{i + 1:04d}.png")
    return n


def main():
    ap = argparse.ArgumentParser(
        description="Render frame animasi Meja Bedah v2 lifestyle creep.")
    ap.add_argument("--segments", required=True,
                    help="vo_segments.json (start/end per beat)")
    ap.add_argument("--vo", required=True, help="file VO (wav) untuk deteksi jeda")
    ap.add_argument("--out", required=True, help="direktori output frame")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--transition", type=float, default=0.45,
                    help="durasi transisi xfade (dtk)")
    ap.add_argument("--beat", type=int, default=0,
                    help="render 1 beat saja (0 = semua)")
    args = ap.parse_args()

    segs = load_segments(args.segments)
    sil = detect_silences(args.vo)
    out = Path(args.out)
    manifest = {"fps": args.fps, "transition": args.transition,
                "segments": segs, "beats": [], "xfade_offsets": []}
    bounds = [0.0]
    for s in segs:
        bounds.append(bounds[-1] + (s["end"] - s["start"]))
    manifest["xfade_offsets"] = bounds[1:-1]
    manifest["transitions"] = TRANSITIONS
    for b in range(1, 9):
        if args.beat and b != args.beat:
            continue
        seg = segs[b - 1]
        dur = seg["end"] - seg["start"]
        P, _n = phrase_starts_from(sil, seg["start"], seg["end"])
        n = render_beat(b, P, dur, out / f"b{b}", args.fps, args.transition)
        manifest["beats"].append({"beat": b, "start": seg["start"],
                                  "end": seg["end"], "dur": dur,
                                  "frames": n, "phrases": P})
        print(f"beat {b}: {n} frame ({dur:.2f} dtk, {len(P)} frasa)")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"manifest -> {out / 'manifest.json'}")


if __name__ == "__main__":
    main()
