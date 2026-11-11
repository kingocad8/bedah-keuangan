#!/usr/bin/env python3
"""Rakit reel lifestyle creep v2 MOTION: 8 urutan frame animasi (Meja Bedah v2)
+ VO ElevenLabs + bed Driving Ambition (Mixkit) + SFX.

Video: image-sequence per beat -> rantai xfade ffmpeg (transisi slide/wipe/
fade 0,45 dtk di tiap batas segmen). Offset xfade = batas kumulatif segmen
(dari manifest.json animator) — jam animasi beat baru mulai tepat di batas
segmen, sinkron dengan VO.

Audio: rantai yang SAMA PERSIS dengan build_reel.py (VO loudnorm I=-14,
musik Driving Ambition jendela 20-86 dtk + ducking ringan, whoosh di tiap
batas segmen -0,15 dtk, boom di t=0, shimmer di awal beat 8, peak <= -0,5 dB).
Audio stereo 48 kHz. Video 1080x1920 30fps.

Pemakaian:
  python3 build_motion.py                       # dari manifest default
  python3 build_motion.py --frames DIR --vo FILE --segments FILE --out FILE
"""
import argparse
import json
import subprocess
from pathlib import Path

BASE = Path.home() / "workspace" / "bedah-keuangan"
REEL = BASE / "reels" / "batch-nov-2026" / "lifestyle-creep-v2"
WORK = REEL / "work"
FRAMES = WORK / "motion-frames"
VO = WORK / "vo_trimmed.wav"
SEGMENTS = WORK / "vo_segments.json"
MUSIC = BASE / "musik" / "driving-ambition.mp3"
SFX = BASE / "reels" / "asuransi-vs-investasi"
OUT = REEL / "lifestyle-creep-v2-motion-test.mp4"
FPS = 30
T = 0.45  # durasi transisi xfade


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=str(FRAMES))
    ap.add_argument("--vo", default=str(VO))
    ap.add_argument("--segments", default=str(SEGMENTS))
    ap.add_argument("--music", default=str(MUSIC))
    ap.add_argument("--sfx", default=str(SFX))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    frames_dir = Path(args.frames)
    manifest = json.loads((frames_dir / "manifest.json").read_text())
    beats = manifest["beats"]
    offsets = manifest["xfade_offsets"]
    transitions = manifest["transitions"]
    segs = json.load(open(args.segments))["segments"]
    assert len(beats) == 8 and len(offsets) == 7 and len(transitions) == 7
    assert [b["beat"] for b in beats] == list(range(1, 9))

    # ---------- video: 8 image-sequence + rantai xfade ----------
    total_frames = sum(b["frames"] for b in beats)
    dur = total_frames / FPS - 7 * T
    vparts = []
    for i in range(1, 9):
        vparts.append(f"[{i - 1}:v]format=yuv420p[v{i}]")
    chain = "[v1]"
    for k in range(7):
        nxt = k + 2
        chain += (f"[v{nxt}]xfade=transition={transitions[k]}:"
                  f"duration={T}:offset={offsets[k]:.6f}[x{k + 1}];"
                  f"[x{k + 1}]")
    chain += "format=yuv420p[vout]"
    vfilter = ";".join(vparts + [chain])

    # ---------- audio (verbatim dari build_reel.py) ----------
    cuts = [s[1] for s in segs[:-1]]
    aparts = []
    aparts.append("[8:a]loudnorm=I=-14:TP=-1.5:LRA=11:linear=true,"
                  "pan=stereo|c0=c0|c1=c0,asplit=2[vo][vosc]")
    aparts.append("[9:a]atrim=start=20:end=86.06,asetpts=PTS-STARTPTS,volume=0.4467[music];"
                  "[music][vosc]sidechaincompress=threshold=0.2:ratio=2:attack=20:"
                  "release=150[mduck]")
    sfx_branches = []
    for j, c in enumerate(cuts):
        delay = max(0, int((c - 0.15) * 1000))
        aparts.append(f"[10:a]adelay={delay}:all=1,volume=0.7071[wh{j}]")
        sfx_branches.append(f"[wh{j}]")
    aparts.append("[11:a]adelay=0:all=1,volume=0.7071[boom]")
    sfx_branches.append("[boom]")
    aparts.append(f"[12:a]adelay={int(segs[7][0] * 1000)}:all=1,volume=0.7071[shim]")
    sfx_branches.append("[shim]")
    mix_ins = "[vo][mduck]" + "".join(sfx_branches)
    fade_st = dur - 0.4
    aparts.append(
        f"{mix_ins}amix=inputs={2 + len(sfx_branches)}:normalize=0,"
        f"alimiter=limit=0.89:level=false,afade=t=out:st={fade_st:.2f}:d=0.4,"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,aresample=48000[aout]"
    )
    filt = vfilter + ";" + ";".join(aparts)

    inputs = []
    for i in range(1, 9):
        inputs += ["-framerate", str(FPS), "-i",
                   str(frames_dir / f"b{i}" / "%04d.png")]
    inputs += ["-i", args.vo, "-i", args.music,
               "-i", f"{args.sfx}/sfx_whoosh.wav",
               "-i", f"{args.sfx}/sfx_boom_soft.wav",
               "-i", f"{args.sfx}/sfx_shimmer.wav"]

    cmd = (["ffmpeg", "-v", "error", "-y"] + inputs +
           ["-filter_complex", filt,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            "-t", f"{dur:.3f}", args.out])
    Path(WORK / "build_motion_cmd.txt").write_text(
        " ".join(cmd) + "\n\nFILTER:\n" + filt + "\n")
    print(f"durasi video: {dur:.3f} dtk ({total_frames} frame - 7 x {T} dtk)")
    print(f"offset xfade: {[round(o, 3) for o in offsets]}")
    print(f"transisi: {transitions}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-1000:] if r.stdout else "")
    print(r.stderr[-3000:] if r.stderr else "")
    print("returncode:", r.returncode)
    if r.returncode == 0:
        print("OK ->", args.out)


if __name__ == "__main__":
    main()
