#!/usr/bin/env python3
"""Full Clear "HOW TO" short: numbered steps synced to the host's voice.

The voiceover must have a [pause] between the intro, each step and the outro, so the steps can be
synced from the silences (fallback: even split).

Usage: python3 tools/howto_short.py content/howto/<id>.json
{
  "host": "Dev",
  "title": "Add an SSD to your PS5",
  "subtitle": "PS5 Slim & Pro · 8 steps",
  "image": "brand/howto/ssd.png",            # our own illustration (never Rockstar content)
  "image_credit": "Illustration",
  "steps": ["Turn off, unplug, touch metal", "..."],
  "outro": "Only a supported Gen4 SSD with a heatsink",
  "source": "Steps: PlayStation Support",
  "voiceover": "videos/howto/....mp3",
  "output": "videos/howto/....mp4"
}
"""
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = '/usr/share/fonts/opentype/inter/'
W, H, FPS, END = 1080, 1920, 30, 2.2
PINK, TEAL, WHITE, MUTED = (255, 62, 165), (54, 241, 225), (246, 239, 250), (200, 185, 215)


def p(x): return x if os.path.isabs(x) else os.path.join(ROOT, x)
def font(n, s): return ImageFont.truetype(F + n, s)


def wrap(d, text, fnt, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fnt) <= width: cur = t
        else: out.append(cur); cur = w
    return out + [cur]


def speech_chunks(vo):
    """Return [(start, end)] of speech between silences >= 0.25 s."""
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', vo, '-af', 'silencedetect=noise=-32dB:d=0.25', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vo]))
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    chunks, t = [], 0.0
    for s, e in zip(starts, ends):
        if s - t > 0.3: chunks.append((t, s))
        t = e
    if dur - t > 0.3: chunks.append((t, dur))
    return chunks, dur


def render(ep):
    vo = p(ep['voiceover'])
    chunks, talk = speech_chunks(vo)
    n = len(ep['steps'])
    # boundaries = the n+1 longest gaps between speech chunks (the [pause] tags), in time order
    gaps = sorted([(chunks[i + 1][0] - chunks[i][1], chunks[i + 1][0]) for i in range(len(chunks) - 1)], reverse=True)
    if ep.get('timings'):      # manual override: [step1_start, ..., stepN_start, outro_start]
        step_starts, outro_start = ep['timings'][:n], ep['timings'][n]
    elif len(gaps) >= n + 1:
        bounds = sorted(g[1] for g in gaps[:n + 1])
        step_starts, outro_start = bounds[:n], bounds[n]
    else:                      # fallback: even split
        seg = talk / (n + 2)
        step_starts = [seg * (i + 1) for i in range(n)]
        outro_start = seg * (n + 1)
    total = talk + 0.5 + END

    base = Image.new('RGB', (W, H)); px = base.load()
    for y in range(H):
        c = tuple(int(a + (b - a) * y / H) for a, b in zip((20, 8, 31), (50, 14, 72)))
        for x in range(W): px[x, y] = c
    base = base.convert('RGBA'); d = ImageDraw.Draw(base)
    d.rounded_rectangle([60, 110, 290, 176], 18, fill=TEAL)
    d.text((175, 143), 'HOW TO', font=font('Inter-Black.otf', 40), fill=(20, 8, 31), anchor='mm')
    y = 200
    for line in wrap(d, ep['title'].upper(), font('Inter-Black.otf', 76), W - 120):
        d.text((60, y), line, font=font('Inter-Black.otf', 76), fill=WHITE); y += 88
    d.text((60, y + 4), ep.get('subtitle', ''), font=font('Inter-ExtraBold.otf', 40), fill=MUTED); y += 70
    img = Image.open(p(ep['image'])).convert('RGB')
    iw = W - 80; ih = int(img.height * iw / img.width)
    if ih > 470: ih = 470
    img = img.resize((iw, int(img.height * iw / img.width)), Image.LANCZOS).crop((0, 0, iw, ih))
    base.paste(img, (40, y)); iy2 = y + ih
    d.text((W - 50, iy2 + 10), ep.get('image_credit', ''), font=font('Inter-SemiBold.otf', 26), fill=MUTED, anchor='ra')
    step_y = iy2 + 70
    # host frame
    loop = p(f"brand/hosts/{ep['host'].lower()}.mp4")
    d.rounded_rectangle([50, H - 450, 442, H - 58], 36, fill=PINK)
    d.text((470, H - 330), ep['host'].upper(), font=font('Inter-Black.otf', 56), fill=WHITE)
    d.text((470, H - 262), ep.get('source', ''), font=font('Inter-SemiBold.otf', 28), fill=MUTED)

    out = p(ep['output']); os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out.replace('.mp4', '.nohost.mp4')
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', vo, '-filter_complex', f'[1:a]apad,atrim=0:{total},loudnorm=I=-14:TP=-1.5[a]', '-map', '0:v', '-map', '[a]',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                           '-ar', '48000', '-t', str(total), tmp], stdin=subprocess.PIPE)
    big = font('Inter-Black.otf', 64); num = font('Inter-Black.otf', 46)
    for k in range(int(total * FPS)):
        t = k / FPS
        f = base.copy(); fd = ImageDraw.Draw(f)
        cur = max([i for i, s in enumerate(step_starts) if t >= s], default=-1)
        if t >= outro_start: cur = n
        # progress dots
        for i in range(n):
            cx = 60 + i * 52
            fd.ellipse([cx, step_y - 40, cx + 30, step_y - 10], fill=(PINK if i <= cur and cur < n else (TEAL if cur == n else (70, 45, 95))))
        if 0 <= cur < n:
            a = min(1.0, (t - step_starts[cur]) / 0.2)
            fd.text((60, step_y + 10), f'STEP {cur + 1}/{n}', font=num, fill=PINK)
            yy = step_y + 80
            for line in wrap(fd, ep['steps'][cur], big, W - 120):
                fd.text((60, yy), line, font=big, fill=tuple(int(v * a + 40 * (1 - a)) for v in WHITE)); yy += 76
        elif cur == n:
            fd.text((60, step_y + 10), '⚠ IMPORTANT'.replace('⚠ ', ''), font=num, fill=TEAL)
            yy = step_y + 80
            for line in wrap(fd, ep['outro'], big, W - 120):
                fd.text((60, yy), line, font=big, fill=WHITE); yy += 76
        if t >= total - END:
            a = min(1.0, (t - (total - END)) / 0.3)
            ov = Image.new('RGBA', (W, H), (14, 6, 22, int(225 * a))); od = ImageDraw.Draw(ov)
            od.text((W / 2, 860), 'FULL CLEAR', font=font('Inter-Black.otf', 120), fill=PINK + (int(255 * a),), anchor='mm')
            od.text((W / 2, 990), '@fullclearmap', font=font('Inter-Black.otf', 70), fill=WHITE + (int(255 * a),), anchor='mm')
            od.text((W / 2, 1100), 'Full guide: link in bio', font=font('Inter-Black.otf', 52), fill=TEAL + (int(255 * a),), anchor='mm')
            f.alpha_composite(ov)
        ff.stdin.write(f.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()
    if os.path.exists(loop):
        mask = out.replace('.mp4', '.mask.png')
        m = Image.new('L', (380, 380), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 379, 379], 30, fill=255); m.save(mask)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-stream_loop', '-1', '-i', loop, '-loop', '1', '-i', mask, '-filter_complex',
                        f"[1:v]scale=380:380,fps={FPS},format=rgba[h];[2:v]format=gray,scale=380:380[m];[h][m]alphamerge[hm];"
                        f"[0:v][hm]overlay=56:{H - 444}:enable='lt(t,{total - END})':shortest=1[v]",
                        '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
                        '-t', str(total), '-movflags', '+faststart', out], check=True)
        os.remove(tmp); os.remove(mask)
    else:
        os.replace(tmp, out)
    print(out, f'{total:.1f}s', f'chunks={len(chunks)}')


if __name__ == '__main__':
    render(json.load(open(sys.argv[1])))
