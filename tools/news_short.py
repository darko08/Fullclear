#!/usr/bin/env python3
"""Full Clear "GTA 6 NEWS" short generator (cheap daily video, ~1 Runway credit for the voice).

Layout (1080x1920): headline card · official image (unmodified, credited) · bullets appearing
one by one · host badge · end card. Voice comes from the host's fixed voice (content/CREW.md).

Usage:  python3 tools/news_short.py content/news/<episode>.json
{
  "host": "Nia",
  "headline": "GTA 6 BROKE PRE-ORDER RECORDS",
  "image": "page/media/official/postcards/Vice_City_16x9.jpg",   # official, shown unmodified
  "image_credit": "© Rockstar Games",
  "bullets": ["Most pre-ordered game in PS Store history", "..."],
  "source": "Source: PlayStation Blog, Xbox Wire",
  "voiceover": "videos/news/....mp3",
  "output": "videos/news/....mp4"
}
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = '/usr/share/fonts/opentype/inter/'
W, H, FPS, END = 1080, 1920, 30, 2.2
PINK, TEAL, WHITE, MUTED, BG2 = (255, 62, 165), (54, 241, 225), (246, 239, 250), (200, 185, 215), (20, 8, 31)


def p(path):
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def font(n, s):
    return ImageFont.truetype(F + n, s)


def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).strip())


def render(ep):
    vo = p(ep['voiceover'])
    talk = duration(vo)
    total = talk + 0.6 + END
    base = Image.new('RGB', (W, H))
    px = base.load()
    for y in range(H):
        c = tuple(int(a + (b - a) * y / H) for a, b in zip((20, 8, 31), (50, 14, 72)))
        for x in range(W):
            px[x, y] = c
    base = base.convert('RGBA')
    d = ImageDraw.Draw(base)
    # "GTA 6 NEWS" tag + headline
    d.rounded_rectangle([60, 120, 380, 190], 18, fill=PINK)
    d.text((220, 155), 'GTA 6 NEWS', font=font('Inter-Black.otf', 40), fill=WHITE, anchor='mm')
    hf = font('Inter-Black.otf', 76)
    y = 220
    for line in wrap(d, ep['headline'].upper(), hf, W - 120):
        d.text((60, y), line, font=hf, fill=WHITE); y += 88
    # official image, unmodified (only scaled), with credit
    img = Image.open(p(ep['image'])).convert('RGB')
    iw = W - 80
    ih = int(img.height * iw / img.width)
    img = img.resize((iw, ih), Image.LANCZOS)
    iy = y + 30
    base.paste(img, (40, iy))
    d.text((W - 50, iy + ih + 12), ep.get('image_credit', '© Rockstar Games'), font=font('Inter-SemiBold.otf', 28), fill=MUTED, anchor='ra')
    by = iy + ih + 80
    # host badge
    host = Image.open(p(f"brand/crew-{ep['host'].lower()}.png")).convert('RGBA')
    s = min(host.size); host = host.crop(((host.width - s) // 2, 0, (host.width + s) // 2, s)).resize((170, 170), Image.LANCZOS)
    mask = Image.new('L', (170, 170), 0); ImageDraw.Draw(mask).ellipse([0, 0, 170, 170], fill=255)
    badge = Image.new('RGBA', (186, 186), (0, 0, 0, 0)); ImageDraw.Draw(badge).ellipse([0, 0, 185, 185], fill=TEAL)
    badge.paste(host, (8, 8), mask)
    loop = p(f"brand/hosts/{ep['host'].lower()}.mp4")
    has_loop = os.path.exists(loop)
    if has_loop:   # talking host goes in a 380px rounded frame bottom-left (added after rendering)
        d.rounded_rectangle([50, H - 450, 50 + 392, H - 450 + 392], 36, fill=TEAL)
        d.text((470, H - 330), ep['host'].upper(), font=font('Inter-Black.otf', 56), fill=WHITE)
        d.text((470, H - 262), ep.get('source', ''), font=font('Inter-SemiBold.otf', 28), fill=MUTED)
    else:
        base.alpha_composite(badge, (60, H - 330))
        d.text((270, H - 270), ep['host'].upper(), font=font('Inter-Black.otf', 46), fill=WHITE)
        d.text((270, H - 212), ep.get('source', ''), font=font('Inter-SemiBold.otf', 28), fill=MUTED)

    bullets = ep['bullets']
    bf = font('Inter-ExtraBold.otf', 50)
    slot = talk / (len(bullets) + 1)        # first slot = headline read
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-i', vo, '-filter_complex', f'[1:a]apad,atrim=0:{total},loudnorm=I=-14:TP=-1.5[a]',
                           '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', str(total), '-movflags', '+faststart', p(ep['output'])],
                          stdin=subprocess.PIPE)
    os.makedirs(os.path.dirname(p(ep['output'])), exist_ok=True)
    for n in range(int(total * FPS)):
        t = n / FPS
        f = base.copy(); fd = ImageDraw.Draw(f)
        yy = by
        for i, b in enumerate(bullets):
            start = slot * (i + 1)
            if t < start:
                break
            a = min(1.0, (t - start) / 0.25)
            col = tuple(int(v * a + 30 * (1 - a)) for v in WHITE)
            fd.text((60, yy), '•', font=bf, fill=PINK)
            for line in wrap(fd, b, bf, W - 160):
                fd.text((110, yy), line, font=bf, fill=col); yy += 62
            yy += 22
        if t >= total - END:
            a = min(1.0, (t - (total - END)) / 0.3)
            ov = Image.new('RGBA', (W, H), (14, 6, 22, int(225 * a))); od = ImageDraw.Draw(ov)
            od.text((W / 2, 860), 'FULL CLEAR', font=font('Inter-Black.otf', 120), fill=PINK + (int(255 * a),), anchor='mm')
            od.text((W / 2, 990), '@fullclearmap', font=font('Inter-Black.otf', 70), fill=WHITE + (int(255 * a),), anchor='mm')
            od.text((W / 2, 1100), 'Follow for daily GTA 6 news', font=font('Inter-Black.otf', 52), fill=TEAL + (int(255 * a),), anchor='mm')
            f.alpha_composite(ov)
        ff.stdin.write(f.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()
    if has_loop:
        out = p(ep['output']); tmp = out.replace('.mp4', '.nohost.mp4'); os.replace(out, tmp)
        mask = out.replace('.mp4', '.mask.png')
        m = Image.new('L', (380, 380), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 379, 379], 30, fill=255); m.save(mask)
        hide = total - END   # host disappears under the end card
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-stream_loop', '-1', '-i', loop, '-loop', '1', '-i', mask,
                        '-filter_complex', f"[1:v]scale=380:380,fps={FPS},format=rgba[h];[2:v]format=gray,scale=380:380[m];[h][m]alphamerge[hm];"
                                           f"[0:v][hm]overlay=56:{H - 444}:enable='lt(t,{hide})':shortest=1[v]",
                        '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
                        '-c:a', 'copy', '-t', str(total), '-movflags', '+faststart', out], check=True)
        os.remove(tmp); os.remove(mask)
    print(p(ep['output']), f'{total:.1f}s')


if __name__ == '__main__':
    render(json.load(open(sys.argv[1])))
