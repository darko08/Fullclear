#!/usr/bin/env python3
"""Full Clear podcasts ("Leonida After Hours", "Keys & Neon"): per-line voice files -> episode video.

Owner's rule (2026-11-18): talking heads alone are boring. EVERY episode shows in-game material behind the talk
(a big B-roll panel) so viewers see what is being discussed. Hosts sit in small tiles under it.

B-roll sources, only these:
  * official Rockstar media (page/media/raw/official/shots|clips, "download and share"): shown UNMODIFIED
    (full frame, no crop, no AI), muted, credit "© Rockstar Games";
  * permitted gameplay (page/permissions.md: CC BY, Discord /submit with licence, creators who said yes), credited.
Never put any of it into AI tools.

Usage:
  python3 tools/podcast.py content/podcast/<id>.json               # 16:9 episode (+ .m4a)
  python3 tools/podcast.py content/podcast/<id>.json --clip 1 13     # 9:16 version of lines 1..13

Episode JSON:
  lines [[host, text], ...]  (text may contain [tags]; stripped for subtitles), audio_dir with 01.mp3 ...
  cast {name: {image}} (optional; default = the crew with brand/crew-<name>.png + talking loops)
  broll {"<line>": {"file": path, "start": sec (video only), "credit": "..."}}  # a line without an entry keeps the previous B-roll
  segments {"<line>": "TITLE"}, sources {"<line>": "Source"}, show, title, episode, output
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from brand import SHOW_HOSTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = '/usr/share/fonts/opentype/inter/'
FPS, GAP, LEAD, TAIL = 30, 0.35, 0.6, 1.2
PINK, TEAL, WHITE, MUTED, BG1, BG2 = (255, 62, 165), (54, 241, 225), (246, 239, 250), (185, 166, 201), (20, 8, 31), (58, 18, 85)
IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp')


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


def broll_track(segs, pw, ph, out):
    """segs: [(dur, item)] -> silent video pw x ph. Images shown whole (letterboxed), videos trimmed + scaled, both unmodified."""
    ins, fl = [], []
    # frame-exact lengths on the absolute timeline (per-segment rounding used to drift ~1 frame per line)
    acc, nfr = 0.0, []
    for d, _ in segs:
        nfr.append(round((acc + d) * FPS) - round(acc * FPS)); acc += d
    for k, (d, it) in enumerate(segs):
        f = p(it['file'])
        if f.lower().endswith(IMG_EXT):
            ins += ['-loop', '1', '-t', f'{d:.3f}', '-i', f]
        else:
            ins += ['-ss', f"{it.get('start', 0):.2f}", '-t', f'{d:.3f}', '-i', f]
        fl.append(f'[{k}:v]scale={pw}:{ph}:force_original_aspect_ratio=decrease,pad={pw}:{ph}:(ow-iw)/2:(oh-ih)/2:black,'
                  f'setsar=1,fps={FPS},format=yuv420p,tpad=stop_mode=clone:stop_duration={d + 1:.3f},trim=end_frame={nfr[k]},setpts=PTS-STARTPTS[s{k}]')
    fl.append(''.join(f'[s{k}]' for k in range(len(segs))) + f'concat=n={len(segs)}:v=1:a=0[v]')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', '[v]', '-an',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', out], check=True)


def build(ep, first, last, vertical):
    cast = list(ep['cast']) if ep.get('cast') else ['Scout', 'Nia', 'Mei', 'Dev']
    img_of = lambda c: p(ep['cast'][c].get('image', f'brand/crew-{c.lower()}.png')) if ep.get('cast') else p(f'brand/crew-{c.lower()}.png')
    n = len(cast)
    W, H = (1080, 1920) if vertical else (1920, 1080)
    adir = p(ep['audio_dir'])
    lines = ep['lines'][first - 1:last]
    t, timeline = LEAD, []
    for i, (host, text) in enumerate(lines, start=first):
        f = os.path.join(adir, f'{i:02d}.mp3'); d = dur(f)
        timeline.append(dict(n=i, host=host, text=clean(text), f=f, a=t, b=t + d)); t += d + GAP
    total = t - GAP + TAIL
    tag = f'.clip{first}-{last}' if vertical else ''
    out = p(ep['output']).replace('.mp4', f'{tag}.mp4'); os.makedirs(os.path.dirname(out), exist_ok=True)

    # ---- audio
    wav = out.replace('.mp4', '.wav')
    inputs, filt = [], []
    for k, s in enumerate(timeline):
        inputs += ['-i', s['f']]; filt.append(f'[{k}:a]aresample=48000,adelay={int(s["a"] * 1000)}|{int(s["a"] * 1000)}[a{k}]')
    filt.append(''.join(f'[a{k}]' for k in range(len(timeline))) + f'amix=inputs={len(timeline)}:normalize=0,apad,atrim=0:{total},loudnorm=I=-16:TP=-1.5[out]')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]', '-ac', '2', wav], check=True)

    # ---- layout
    if vertical:
        px_, py_, pw, ph = 0, 420, 1080, 608                     # B-roll panel
        ts = 300 if n <= 2 else 220
        gap = 120 if n <= 2 else 30
        x0 = (W - (n * ts + (n - 1) * gap)) // 2
        pos = {c: (x0 + i * (ts + gap), 1080) for i, c in enumerate(cast)}
        name_size, sub_y, sub_size = 36, 1520, 54
    else:
        px_, py_, pw, ph = 60, 190, 1280, 720
        if n <= 2:
            ts = 300; pos = {c: (1460, 190 + i * 390) for i, c in enumerate(cast)}
        else:
            ts = 230; pos = {c: (1400 + (i % 2) * 260, 190 + (i // 2) * 330) for i, c in enumerate(cast)}
        name_size, sub_y, sub_size = 32, 935, 40

    if not SHOW_HOSTS:   # voice only (owner 2026-11-20): no host tiles, the footage gets the space
        cast, pos = [], {}
        if vertical:
            px_, py_, pw, ph = 0, 400, 1080, 810
            sub_y, sub_size = 1320, 56
        else:
            px_, py_, pw, ph = 320, 190, 1280, 720
            sub_y, sub_size = 950, 42
    # B-roll per line (inherit previous), consumed sequentially so repeated videos move forward
    br = {int(k): v for k, v in ep.get('broll', {}).items()}
    cur_item, seq, used = None, [], {}
    for idx, s in enumerate(timeline):
        it = br.get(s['n']) or cur_item or next((br[k] for k in sorted(br) if k >= s['n']), None)
        cur_item = it
        a = 0.0 if idx == 0 else s['a']
        b = timeline[idx + 1]['a'] if idx + 1 < len(timeline) else total
        seq.append((b - a, it, s['n']))
    segs, credit_for = [], {}
    for d, it, nline in seq:
        item = dict(it)
        if not item['file'].lower().endswith(IMG_EXT):
            key = item['file'] + str(item.get('start', 0))
            item['start'] = item.get('start', 0) + used.get(key, 0); used[key] = used.get(key, 0) + d
            fdur = dur(p(item['file']))
            if item['start'] > fdur - 0.5:   # clip ran out (short official clips): start it again, never past the end
                item['start'] = it.get('start', 0) if it.get('start', 0) < fdur - 0.5 else 0.0
        segs.append((d, item)); credit_for[nline] = it.get('credit', '© Rockstar Games')
    track = out.replace('.mp4', '.broll.mp4'); broll_track(segs, pw, ph, track)

    portraits = {c: Image.open(img_of(c)).convert('RGB').resize((ts, ts), Image.LANCZOS) for c in cast}
    dim = {c: ImageEnhance.Brightness(im).enhance(0.38) for c, im in portraits.items()}
    mask = Image.new('L', (ts, ts), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, ts - 1, ts - 1], 28, fill=255)

    base = Image.new('RGB', (W, H)); bp = base.load()
    for y in range(H):
        c = tuple(int(a + (b - a) * y / H) for a, b in zip(BG1, BG2))
        for x in range(W): bp[x, y] = c
    base = base.convert('RGBA'); d = ImageDraw.Draw(base)
    if vertical:
        d.rounded_rectangle([60, 90, 330, 150], 16, fill=PINK)
        d.text((195, 120), ep.get('label', 'PODCAST'), font=font('Inter-Black.otf', 36), fill=BG1, anchor='mm')
        d.text((60, 175), ep['show'], font=font('Inter-Black.otf', 76), fill=WHITE)
        d.text((60, 275), ep['title'], font=font('Inter-ExtraBold.otf', 44), fill=TEAL)
    else:
        d.rounded_rectangle([60, 50, 320, 106], 16, fill=PINK)
        d.text((190, 78), ep.get('label', 'PODCAST'), font=font('Inter-Black.otf', 34), fill=BG1, anchor='mm')
        d.text((350, 42), ep['show'], font=font('Inter-Black.otf', 62), fill=WHITE)
        d.text((62, 128), f"{ep['title']}  ·  {ep['episode']}", font=font('Inter-ExtraBold.otf', 34), fill=TEAL)
    for c in cast:
        x, y = pos[c]
        d.text((x + ts // 2, y + ts + 28), c.upper(), font=font('Inter-Black.otf', name_size), fill=MUTED, anchor='mm')
    d.text((W - 60, H - 45), '@fullclearmap', font=font('Inter-Black.otf', 32), fill=MUTED, anchor='rm')
    # transparent window for the B-roll
    alpha = base.getchannel('A'); ImageDraw.Draw(alpha).rounded_rectangle([px_, py_, px_ + pw - 1, py_ + ph - 1], 0 if vertical else 24, fill=0)
    base.putalpha(alpha)

    segs_t = {int(k): v for k, v in ep.get('segments', {}).items()}
    srcs = {int(k): v for k, v in ep.get('sources', {}).items()}
    seg_for = {x['n']: next((segs_t[k] for k in sorted(segs_t, reverse=True) if k <= x['n']), '') for x in timeline}

    tmp = out.replace('.mp4', '.nohost.mp4')
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-i', track, '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-filter_complex', f'[0:v]pad={W}:{H}:{px_}:{py_}:black[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p[v]', '-map', '[v]',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-t', f'{total:.2f}', tmp], stdin=subprocess.PIPE)
    sub_font = font('Inter-ExtraBold.otf', sub_size)
    cache = {}
    for k in range(int(total * FPS)):
        tt = k / FPS
        s = next((x for x in timeline if x['a'] - 0.15 <= tt < x['b'] + GAP), None)
        key = s['n'] if s else (-1 if tt < LEAD else -2)
        if key not in cache:
            f = base.copy(); fd = ImageDraw.Draw(f)
            speaker = s['host'] if s else None
            for c in cast:
                x, y = pos[c]
                f.paste(portraits[c] if c == speaker else dim[c], (x, y), mask)
                if c == speaker:
                    fd.rounded_rectangle([x - 7, y - 7, x + ts + 6, y + ts + 6], 34, outline=PINK, width=7)
                    fd.text((x + ts // 2, y + ts + 28), c.upper(), font=font('Inter-Black.otf', name_size), fill=PINK, anchor='mm')
            ln = s['n'] if s else (timeline[0]['n'] if tt < LEAD else timeline[-1]['n'])
            cr = credit_for.get(ln, '')
            if cr:   # credit on the B-roll panel, always visible
                cw = fd.textlength(cr, font=font('Inter-Bold.otf', 26)) + 24
                fd.rounded_rectangle([px_ + pw - cw - 14, py_ + ph - 50, px_ + pw - 14, py_ + ph - 14], 10, fill=(14, 6, 22, 200))
                fd.text((px_ + pw - 14 - cw / 2, py_ + ph - 32), cr, font=font('Inter-Bold.otf', 26), fill=WHITE, anchor='mm')
            if s:
                seg = seg_for[s['n']]
                if seg:
                    w = fd.textlength(seg, font=font('Inter-Black.otf', 28)) + 36
                    sx, sy = (px_ + 16, py_ + 16)
                    fd.rounded_rectangle([sx, sy, sx + w, sy + 46], 12, fill=TEAL + (255,))
                    fd.text((sx + w / 2, sy + 23), seg, font=font('Inter-Black.otf', 28), fill=BG1, anchor='mm')
                sl = wrap(fd, s['text'], sub_font, W - 120)
                for j, l in enumerate(sl):
                    fd.text((W / 2, sub_y + j * (sub_size + 12)), l, font=sub_font, fill=WHITE, anchor='mm')
                if srcs.get(s['n']):
                    fd.text((60, H - 45), 'Source: ' + srcs[s['n']], font=font('Inter-SemiBold.otf', 28), fill=MUTED, anchor='lm')
            cache[key] = f.tobytes()
        if tt >= total - TAIL + 0.2:
            a = min(1.0, (tt - (total - TAIL + 0.2)) / 0.4)
            f = Image.frombytes('RGBA', (W, H), cache[key])
            ov = Image.new('RGBA', (W, H), (14, 6, 22, int(240 * a))); od = ImageDraw.Draw(ov)
            od.text((W / 2, H / 2 - 60), 'FULL CLEAR', font=font('Inter-Black.otf', 120), fill=PINK + (int(255 * a),), anchor='mm')
            od.text((W / 2, H / 2 + 70), f"{ep['show'].title()} · @fullclearmap", font=font('Inter-Black.otf', 48 if not vertical else 42), fill=WHITE + (int(255 * a),), anchor='mm')
            f.alpha_composite(ov); ff.stdin.write(f.tobytes())
        else:
            ff.stdin.write(cache[key])
    ff.stdin.close(); ff.wait()

    # ---- talking loops on the crew tiles (crew only)
    ins, fl, last_lbl, n_in = ['-i', tmp], [], '0:v', 1
    m = out.replace('.mp4', '.mask.png'); mask.save(m)
    for j, c in enumerate(cast):
        spans = [(x['a'] - 0.15, x['b']) for x in timeline if x['host'] == c]
        loop = p(f'brand/hosts/{c.lower()}.mp4')
        if not spans or not os.path.exists(loop): continue  # guests (Rosa/Jay) have no loop file
        ins += ['-stream_loop', '-1', '-i', loop, '-loop', '1', '-i', m]; k, km = n_in, n_in + 1; n_in += 2
        en = '+'.join(f'between(t,{a:.2f},{b:.2f})' for a, b in spans)
        x, y = pos[c]
        fl.append(f'[{k}:v]scale={ts}:{ts},fps={FPS},format=rgba[h{j}];[{km}:v]format=gray,scale={ts}:{ts}[m{j}];[h{j}][m{j}]alphamerge[hm{j}]')
        fl.append(f"[{last_lbl}][hm{j}]overlay={x}:{y}:enable='{en}':shortest=1[v{j}]"); last_lbl = f'v{j}'
    if not fl: fl, last_lbl = ['[0:v]null[vv]'], 'vv'
    ins += ['-i', wav]; ka = n_in
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', f'[{last_lbl}]', '-map', f'{ka}:a',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                    '-t', f'{total:.2f}', '-movflags', '+faststart', out], check=True)
    if not vertical:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wav, '-c:a', 'aac', '-b:a', '160k', out.replace('.mp4', '.m4a')], check=True)
    for f in (tmp, m, wav, track): os.remove(f)
    print(out, f'{total:.1f}s')


if __name__ == '__main__':
    ep = json.load(open(sys.argv[1]))
    if '--clip' in sys.argv:
        i = sys.argv.index('--clip'); build(ep, int(sys.argv[i + 1]), int(sys.argv[i + 2]), True)
    else:
        build(ep, 1, len(ep['lines']), False)
