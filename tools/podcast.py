#!/usr/bin/env python3
"""Full Clear podcast "Leonida After Hours": stitch per-line voice files into an episode (audio + studio video).

Usage:
  python3 tools/podcast.py content/podcast/<id>.json            # 16:9 full episode (+ .m4a audio)
  python3 tools/podcast.py content/podcast/<id>.json --clip 8 10  # 9:16 social clip of lines 8..10 (1-based)

Episode JSON: lines [[host, text], ...] (text may contain [tags]; stripped for subtitles),
audio_dir with NN.mp3 per line (01.mp3 ...), segments {"line_no": "TITLE"}, sources {"line_no": "Source"},
show, title, episode, output.
Video: the 4 crew portraits; the speaker's tile lights up and plays their talking loop (brand/hosts/<name>.mp4),
subtitles, segment card, source on screen. Our own crew art only (never Rockstar content).
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = '/usr/share/fonts/opentype/inter/'
FPS, GAP, LEAD, TAIL = 30, 0.35, 0.6, 1.2
PINK, TEAL, WHITE, MUTED, BG1, BG2 = (255, 62, 165), (54, 241, 225), (246, 239, 250), (185, 166, 201), (20, 8, 31), (58, 18, 85)

def p(x): return x if os.path.isabs(x) else os.path.join(ROOT, x)
def font(n, s): return ImageFont.truetype(F + n, s)
def clean(t): return re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]', ' ', t)).strip()
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))


def wrap(d, text, fnt, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fnt) <= width: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def build(ep, first, last, vertical):
    CREW = list(ep['cast']) if ep.get('cast') else ['Scout', 'Nia', 'Mei', 'Dev']
    img_of = lambda c: p(ep['cast'][c]['image']) if ep.get('cast') else p(f'brand/crew-{c.lower()}.png')
    n = len(CREW)
    W, H = (1080, 1920) if vertical else (1920, 1080)
    adir = p(ep['audio_dir'])
    lines = ep['lines'][first - 1:last]
    # timeline
    t, timeline = LEAD, []
    for i, (host, text) in enumerate(lines, start=first):
        f = os.path.join(adir, f'{i:02d}.mp3'); d = dur(f)
        timeline.append(dict(n=i, host=host, text=clean(text), f=f, a=t, b=t + d)); t += d + GAP
    total = t - GAP + TAIL
    tag = f'.clip{first}-{last}' if vertical else ''
    out = p(ep['output']).replace('.mp4', f'{tag}.mp4'); os.makedirs(os.path.dirname(out), exist_ok=True)

    # audio: lines placed on the timeline
    wav = out.replace('.mp4', '.wav')
    inputs, filt = [], []
    for k, s in enumerate(timeline):
        inputs += ['-i', s['f']]; filt.append(f'[{k}:a]aresample=48000,adelay={int(s["a"] * 1000)}|{int(s["a"] * 1000)}[a{k}]')
    filt.append(''.join(f'[a{k}]' for k in range(len(timeline))) + f'amix=inputs={len(timeline)}:normalize=0,apad,atrim=0:{total},loudnorm=I=-16:TP=-1.5[out]')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ac', '2', wav], check=True)

    # tile layout
    if vertical and n > 2:
        ts = 440; pos = {CREW[i]: (70 + (i % 2) * 500, 500 + (i // 2) * 500) for i in range(n)}
    elif vertical:
        ts = 460; pos = {CREW[i]: (60 + i * 500, 640) for i in range(n)}
    else:
        ts = 360 if n > 2 else 470; gap = 60 if n > 2 else 160; x0 = (W - (n * ts + (n - 1) * gap)) // 2
        pos = {c: (x0 + i * (ts + gap), 240 if n > 2 else 220) for i, c in enumerate(CREW)}
    portraits = {c: Image.open(img_of(c)).convert('RGB').resize((ts, ts), Image.LANCZOS) for c in CREW}
    dim = {c: ImageEnhance.Brightness(im).enhance(0.38) for c, im in portraits.items()}
    mask = Image.new('L', (ts, ts), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, ts - 1, ts - 1], 34, fill=255)

    base = Image.new('RGB', (W, H)); px = base.load()
    for y in range(H):
        c = tuple(int(a + (b - a) * y / H) for a, b in zip(BG1, BG2))
        for x in range(W): px[x, y] = c
    d = ImageDraw.Draw(base)
    if vertical:
        d.rounded_rectangle([60, 110, 420, 176], 18, fill=PINK)
        d.text((240, 143), 'PODCAST', font=font('Inter-Black.otf', 40), fill=BG1, anchor='mm')
        d.text((60, 210), ep['show'], font=font('Inter-Black.otf', 78), fill=WHITE)
        yy = 310
        for ln in wrap(d, ep['title'], font('Inter-ExtraBold.otf', 46), W - 120):
            d.text((60, yy), ln, font=font('Inter-ExtraBold.otf', 46), fill=TEAL); yy += 58
    else:
        d.rounded_rectangle([70, 60, 330, 116], 16, fill=PINK)
        d.text((200, 88), 'PODCAST', font=font('Inter-Black.otf', 34), fill=BG1, anchor='mm')
        d.text((360, 52), ep['show'], font=font('Inter-Black.otf', 64), fill=WHITE)
        d.text((72, 150), f"{ep['title']}  ·  {ep['episode']}", font=font('Inter-ExtraBold.otf', 38), fill=TEAL)
    for c in CREW:
        x, y = pos[c]
        d.text((x + ts // 2, y + ts + 34), c.upper(), font=font('Inter-Black.otf', 40 if not vertical else 44), fill=MUTED, anchor='mm')
    d.text((W - 60, H - 50), '@fullclearmap', font=font('Inter-Black.otf', 34), fill=MUTED, anchor='rm')

    segs = {int(k): v for k, v in ep.get('segments', {}).items()}
    srcs = {int(k): v for k, v in ep.get('sources', {}).items()}
    seg_for = {x['n']: next((segs[k] for k in sorted(segs, reverse=True) if k <= x['n']), '') for x in timeline}
    src_for = {x['n']: srcs.get(x['n'], '') for x in timeline}

    tmp = out.replace('.mp4', '.nohost.mp4')
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    sub_font = font('Inter-ExtraBold.otf', 50 if not vertical else 56)
    cache = {}
    for k in range(int(total * FPS)):
        tt = k / FPS
        s = next((x for x in timeline if x['a'] - 0.15 <= tt < x['b'] + GAP), None)
        key = s['n'] if s else (-1 if tt < LEAD else -2)
        if key not in cache:
            f = base.copy(); fd = ImageDraw.Draw(f)
            speaker = s['host'] if s else None
            for c in CREW:
                x, y = pos[c]
                f.paste(portraits[c] if c == speaker else dim[c], (x, y), mask)
                if c == speaker:
                    fd.rounded_rectangle([x - 8, y - 8, x + ts + 7, y + ts + 7], 40, outline=PINK, width=8)
                    fd.text((x + ts // 2, y + ts + 34), c.upper(), font=font('Inter-Black.otf', 40 if not vertical else 44), fill=PINK, anchor='mm')
            if s:
                seg = seg_for[s['n']]
                if seg:
                    sy = 210 if not vertical else 420
                    sx = 72 if not vertical else 60
                    w = fd.textlength(seg, font=font('Inter-Black.otf', 30)) + 40
                    if not vertical:
                        sx, sy = W - 70 - w, 66
                    fd.rounded_rectangle([sx, sy, sx + w, sy + 50], 14, fill=TEAL)
                    fd.text((sx + w / 2, sy + 25), seg, font=font('Inter-Black.otf', 30), fill=BG1, anchor='mm')
                sub_w = W - (240 if not vertical else 120)
                sl = wrap(fd, s['text'], sub_font, sub_w)
                y0 = (H - 300 if not vertical else 1590)
                for j, ln in enumerate(sl):
                    fd.text((W / 2, y0 + j * (62 if not vertical else 68)), ln, font=sub_font, fill=WHITE, anchor='mm')
                if src_for[s['n']]:
                    fd.text((60, H - 50), 'Source: ' + src_for[s['n']], font=font('Inter-SemiBold.otf', 30), fill=MUTED, anchor='lm')
            cache[key] = f.tobytes()
        if tt >= total - TAIL + 0.2:
            a = min(1.0, (tt - (total - TAIL + 0.2)) / 0.4)
            f = Image.frombytes('RGB', (W, H), cache[key]).convert('RGBA')
            ov = Image.new('RGBA', (W, H), (14, 6, 22, int(230 * a))); od = ImageDraw.Draw(ov)
            od.text((W / 2, H / 2 - 60), 'FULL CLEAR', font=font('Inter-Black.otf', 120), fill=PINK + (int(255 * a),), anchor='mm')
            od.text((W / 2, H / 2 + 70), 'Leonida After Hours · @fullclearmap', font=font('Inter-Black.otf', 52 if not vertical else 44), fill=WHITE + (int(255 * a),), anchor='mm')
            f.alpha_composite(ov); ff.stdin.write(f.convert('RGB').tobytes())
        else:
            ff.stdin.write(cache[key])
    ff.stdin.close(); ff.wait()

    # talking loops over the active tile
    ins, fl, last_lbl, n_in = ['-i', tmp], [], '0:v', 1
    m = out.replace('.mp4', '.mask.png'); mask.save(m)
    for j, c in enumerate(CREW):
        spans = [(x['a'] - 0.15, x['b']) for x in timeline if x['host'] == c]
        loop = p(f'brand/hosts/{c.lower()}.mp4')
        if not spans or ep.get('cast') or not os.path.exists(loop): continue
        ins += ['-stream_loop', '-1', '-i', loop, '-loop', '1', '-i', m]; k, km = n_in, n_in + 1; n_in += 2
        en = '+'.join(f'between(t,{a:.2f},{b:.2f})' for a, b in spans)
        x, y = pos[c]
        fl.append(f'[{k}:v]scale={ts}:{ts},fps={FPS},format=rgba[h{j}];[{km}:v]format=gray,scale={ts}:{ts}[m{j}];[h{j}][m{j}]alphamerge[hm{j}]')
        fl.append(f"[{last_lbl}][hm{j}]overlay={x}:{y}:enable='{en}':shortest=1[v{j}]"); last_lbl = f'v{j}'
    ins += ['-i', wav]; ka = n_in
    if not fl: fl, last_lbl = ['[0:v]null[vv]'], 'vv'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', f'[{last_lbl}]', '-map', f'{ka}:a',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                    '-t', f'{total:.2f}', '-movflags', '+faststart', out], check=True)
    if not vertical:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wav, '-c:a', 'aac', '-b:a', '160k', out.replace('.mp4', '.m4a')], check=True)
    for f in (tmp, m, wav): os.remove(f)
    print(out, f'{total:.1f}s')


if __name__ == '__main__':
    ep = json.load(open(sys.argv[1]))
    if '--clip' in sys.argv:
        i = sys.argv.index('--clip'); build(ep, int(sys.argv[i + 1]), int(sys.argv[i + 2]), True)
    else:
        build(ep, 1, len(ep['lines']), False)
