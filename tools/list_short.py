#!/usr/bin/env python3
"""Full Clear listicle short ("5 ways Leonida eats your money"): numbered points synced to the host's voice.

Layout (9:16): title + N/5 counter, a B-roll panel (official screenshot shown whole and unmodified with "© Rockstar Games",
or permitted gameplay, credited), the point title with one accent keyword, our own mini graphic that SHOWS the mechanic,
the host tile (talking loop) and the source of every claim. Never put Rockstar content into AI tools.

Usage: python3 tools/list_short.py content/lists/<id>.json
{
  "host": "Nia", "title": "5 WAYS LEONIDA", "accent": "EATS YOUR MONEY",
  "voiceover": "videos/lists/x.mp3",
  "timings": [hook_end, p1_start, p2_start, ..., outro_start],     # seconds in the voiceover
  "points": [{"title": "No cash, no mission", "key": "no mission", "image": "...jpg", "credit": "© Rockstar Games",
              "graphic": {"type": "choice", "items": ["BLOW IT|fast, damaged", "FIND THE CODE|keeps everything"]},
              "source": "Source: IGN preview, Nov 2026"}, ...],
  "outro": "Which one hurts you most?", "cta": "Free map & tracker: link in bio",
  "output": "videos/lists/x.mp4"
}
graphic types: choice (2 cards) · bars ([label|0..1, ...]) · flow ([A, B, C]) · checklist ([lines]) · stat ({"big": "$100", "small": "per fast travel"})
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = '/usr/share/fonts/opentype/inter/'
W, H, FPS, END = 1080, 1920, 30, 2.2
PINK, TEAL, ORANGE, WHITE, MUTED, BG1, BG2 = (255, 62, 165), (54, 241, 225), (255, 140, 40), (246, 239, 250), (190, 175, 210), (20, 8, 31), (50, 14, 72)
PX, PY, PW, PH = 0, 330, 1080, 608


def p(x): return x if os.path.isabs(x) else os.path.join(ROOT, x)
def font(n, s): return ImageFont.truetype(F + n, s)
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))


def wrap(d, text, fnt, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fnt) <= width: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def accent_line(d, xy, text, key, fnt, base=WHITE, acc=ORANGE, anchor_center=True):
    """Draw text with the `key` words in the accent colour (one line, centered)."""
    parts = text.split(key) if key and key in text else [text]
    segs = []
    for i, part in enumerate(parts):
        if part: segs.append((part, base))
        if i < len(parts) - 1: segs.append((key, acc))
    total = sum(d.textlength(s, font=fnt) for s, _ in segs)
    x = xy[0] - total / 2 if anchor_center else xy[0]
    for s, c in segs:
        d.text((x, xy[1]), s, font=fnt, fill=c); x += d.textlength(s, font=fnt)


def graphic(d, g, y, a):
    """Our own mini UI graphic that shows the mechanic. a = 0..1 reveal."""
    col = lambda c: tuple(int(v * a + 20 * (1 - a)) for v in c)
    t = g.get('type')
    if t == 'choice':
        for i, it in enumerate(g['items'][:2]):
            head, _, sub = it.partition('|'); x = 90 + i * 470
            fill = ORANGE if i == 0 else None
            d.rounded_rectangle([x, y, x + 430, y + 150], 22, fill=col(fill) if fill else None, outline=col(TEAL if i else ORANGE), width=5)
            d.text((x + 215, y + 55), head, font=font('Inter-Black.otf', 44), fill=col(BG1 if fill else WHITE), anchor='mm')
            d.text((x + 215, y + 108), sub, font=font('Inter-Bold.otf', 30), fill=col(BG1 if fill else MUTED), anchor='mm')
    elif t == 'bars':
        for i, it in enumerate(g['items'][:3]):
            lab, _, v = it.partition('|'); yy = y + i * 70
            d.text((90, yy + 22), lab, font=font('Inter-Black.otf', 38), fill=col(WHITE), anchor='lm')
            d.rounded_rectangle([330, yy, 990, yy + 44], 14, outline=col(TEAL), width=4)
            d.rounded_rectangle([330, yy, 330 + int(660 * float(v or 0) * a), yy + 44], 14, fill=ORANGE)
    elif t == 'flow':
        items = g['items'][:3]; w = 270; gap = (900 - 3 * w) // 2
        for i, it in enumerate(items):
            x = 90 + i * (w + gap); lit = a * len(items) > i
            d.rounded_rectangle([x, y + 20, x + w, y + 130], 22, fill=ORANGE if lit else None, outline=ORANGE, width=5)
            d.text((x + w / 2, y + 75), it, font=font('Inter-Black.otf', 44), fill=BG1 if lit else WHITE, anchor='mm')
            if i < len(items) - 1:
                d.text((x + w + gap / 2, y + 75), '→', font=font('Inter-Black.otf', 56), fill=col(WHITE), anchor='mm')
    elif t == 'checklist':
        for i, it in enumerate(g['items'][:3]):
            if a * len(g['items']) <= i: break
            yy = y + i * 64
            d.rounded_rectangle([90, yy, 134, yy + 44], 10, fill=ORANGE)
            d.text((112, yy + 22), '✓', font=font('Inter-Black.otf', 32), fill=BG1, anchor='mm')
            d.text((160, yy + 22), it, font=font('Inter-Bold.otf', 38), fill=WHITE, anchor='lm')
    elif t == 'stat':
        d.text((W / 2, y + 60), g['big'], font=font('Inter-Black.otf', 120), fill=col(ORANGE), anchor='mm')
        d.text((W / 2, y + 150), g.get('small', ''), font=font('Inter-Bold.otf', 38), fill=col(WHITE), anchor='mm')


def render(ep):
    vo = p(ep['voiceover']); talk = dur(vo); n = len(ep['points'])
    tm = ep['timings']; hook_end, starts, outro_start = tm[0], tm[1:n + 1], tm[n + 1]
    total = talk + 0.4 + END
    out = p(ep['output']); os.makedirs(os.path.dirname(out), exist_ok=True)

    # B-roll track: hook image (first point's image) then each point's image/clip, shown whole
    seq = [(0.0, starts[0], ep.get('hook_image', ep['points'][0]))] + \
          [(starts[i], (starts[i + 1] if i + 1 < n else total), ep['points'][i]) for i in range(n)]
    ins, fl = [], []
    for k, (a, b, it) in enumerate(seq):
        d = b - a; f = p(it['image'] if isinstance(it, dict) and 'image' in it else it)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): ins += ['-loop', '1', '-t', f'{d:.3f}', '-i', f]
        else: ins += ['-ss', f"{it.get('start', 0):.2f}", '-t', f'{d:.3f}', '-i', f]
        fl.append(f'[{k}:v]scale={PW}:{PH}:force_original_aspect_ratio=decrease,pad={PW}:{PH}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps={FPS},'
                  f'format=yuv420p,trim=duration={d:.3f},setpts=PTS-STARTPTS[s{k}]')
    fl.append(''.join(f'[s{k}]' for k in range(len(seq))) + f'concat=n={len(seq)}:v=1:a=0[v]')
    track = out.replace('.mp4', '.broll.mp4')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', '[v]', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', track], check=True)

    base = Image.new('RGB', (W, H)); bp = base.load()
    for y in range(H):
        c = tuple(int(a + (b - a) * y / H) for a, b in zip(BG1, BG2))
        for x in range(W): bp[x, y] = c
    base = base.convert('RGBA'); d = ImageDraw.Draw(base)
    d.rounded_rectangle([40, 120, W - 40, 290], 26, outline=TEAL, width=4, fill=(14, 6, 22))
    d.text((80, 160), ep['title'], font=font('Inter-Black.otf', 54), fill=WHITE, anchor='lm')
    d.text((80, 240), ep['accent'], font=font('Inter-Black.otf', 54), fill=ORANGE, anchor='lm')
    hx, hy, hs = 60, 1430, 300
    d.rounded_rectangle([hx - 6, hy - 6, hx + hs + 5, hy + hs + 5], 34, fill=PINK)
    d.text((hx + hs + 40, hy + 120), ep['host'].upper(), font=font('Inter-Black.otf', 52), fill=WHITE)
    d.text((W - 50, H - 50), '@fullclearmap', font=font('Inter-Black.otf', 32), fill=MUTED, anchor='rm')
    alpha = base.getchannel('A'); ImageDraw.Draw(alpha).rectangle([PX, PY, PX + PW - 1, PY + PH - 1], fill=0); base.putalpha(alpha)

    tmp = out.replace('.mp4', '.nohost.mp4')
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-i', track, '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', vo, '-filter_complex', f'[0:v]pad={W}:{H}:{PX}:{PY}:black[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p[v];'
                           f'[2:a]apad,atrim=0:{total},loudnorm=I=-14:TP=-1.5,aresample=48000[a]', '-map', '[v]', '-map', '[a]',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{total:.2f}', tmp],
                          stdin=subprocess.PIPE)
    big = font('Inter-Black.otf', 66)
    for k in range(int(total * FPS)):
        t = k / FPS
        f = base.copy(); fd = ImageDraw.Draw(f)
        cur = max([i for i, s in enumerate(starts) if t >= s], default=-1)
        if t >= outro_start: cur = n
        if 0 <= cur < n:
            pt = ep['points'][cur]; a = min(1.0, (t - starts[cur]) / 0.35)
            badge = f'{cur + 1}/{n}'
            fd.rounded_rectangle([W - 190, 150, W - 70, 230], 18, fill=ORANGE)
            fd.text((W - 130, 190), badge, font=font('Inter-Black.otf', 46), fill=BG1, anchor='mm')
            lines = wrap(fd, pt['title'], big, W - 120)
            for j, ln in enumerate(lines[:2]):
                accent_line(fd, (W / 2, 975 + j * 80), ln, pt.get('key', ''), big)
            graphic(fd, pt.get('graphic', {}), 975 + 80 * min(2, len(lines)) + 30, a)
            fd.text((W / 2, 1385), pt.get('source', ''), font=font('Inter-SemiBold.otf', 28), fill=MUTED, anchor='mm')
            cr = pt.get('credit', '© Rockstar Games')
        elif cur == n:
            for j, ln in enumerate(wrap(fd, ep['outro'], big, W - 120)[:3]):
                fd.text((W / 2, 1000 + j * 80), ln, font=big, fill=WHITE, anchor='mm')
            cr = ep['points'][-1].get('credit', '© Rockstar Games')
        else:
            fd.text((W / 2, 1060), ep.get('hook', ''), font=big, fill=WHITE, anchor='mm')
            cr = ep['points'][0].get('credit', '© Rockstar Games')
        cw = fd.textlength(cr, font=font('Inter-Bold.otf', 26)) + 24
        fd.rounded_rectangle([PX + PW - cw - 14, PY + PH - 50, PX + PW - 14, PY + PH - 14], 10, fill=(14, 6, 22, 200))
        fd.text((PX + PW - 14 - cw / 2, PY + PH - 32), cr, font=font('Inter-Bold.otf', 26), fill=WHITE, anchor='mm')
        if t >= total - END:
            a = min(1.0, (t - (total - END)) / 0.3)
            ov = Image.new('RGBA', (W, H), (14, 6, 22, int(235 * a))); od = ImageDraw.Draw(ov)
            od.text((W / 2, 860), 'FULL CLEAR', font=font('Inter-Black.otf', 120), fill=PINK + (int(255 * a),), anchor='mm')
            od.text((W / 2, 990), '@fullclearmap', font=font('Inter-Black.otf', 70), fill=WHITE + (int(255 * a),), anchor='mm')
            od.text((W / 2, 1100), ep.get('cta', ''), font=font('Inter-Black.otf', 48), fill=TEAL + (int(255 * a),), anchor='mm')
            f.alpha_composite(ov)
        ff.stdin.write(f.tobytes())
    ff.stdin.close(); ff.wait()

    loop = p(f"brand/hosts/{ep['host'].lower()}.mp4"); m = out.replace('.mp4', '.mask.png')
    mk = Image.new('L', (hs, hs), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, hs - 1, hs - 1], 30, fill=255); mk.save(m)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-stream_loop', '-1', '-i', loop, '-loop', '1', '-i', m, '-filter_complex',
                    f"[1:v]scale={hs}:{hs},fps={FPS},format=rgba[h];[2:v]format=gray,scale={hs}:{hs}[mm];[h][mm]alphamerge[hm];"
                    f"[0:v][hm]overlay={hx}:{hy}:enable='lt(t,{total - END})':shortest=1[v]", '-map', '[v]', '-map', '0:a',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-t', f'{total:.2f}', '-movflags', '+faststart', out], check=True)
    for x in (tmp, m, track): os.remove(x)
    print(out, f'{total:.1f}s')


if __name__ == '__main__':
    render(json.load(open(sys.argv[1])))
