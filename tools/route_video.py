#!/usr/bin/env python3
"""Full Clear "How long does it take..." short generator.

Draws routes on our own map image one after another, with a timer counting up for each
travel mode, a host badge, captions and an end card, then mixes in the host's voiceover.

Usage:
    python3 tools/route_video.py content/series-how-long/episode.json

Episode JSON (see content/series-how-long/example-episode.json):
{
  "title": "How long to cross Leonida?",
  "host": "Dev",                       # Scout | Nia | Mei | Dev (picks brand/crew-<host>.png)
  "map": "path/to/our-map.png",        # OUR OWN stylised map (never a screenshot of someone else's)
  "voiceover": "path/to/vo.mp3",       # optional
  "routes": [
    {"mode": "ON FOOT", "minutes": 178, "color": "#b88cff", "points": [[0.1,0.9],[0.4,0.5],[0.8,0.1]]},
    ...
  ],
  "output": "videos/03-how-long/fullclear-03-how-long.mp4"
}
Points are fractions of the map image (0,0 = top-left, 1,1 = bottom-right).
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = '/usr/share/fonts/opentype/inter/'
W, H, FPS = 1080, 1920, 30
INTRO, PER_ROUTE, HOLD, END = 1.5, 3.2, 2.0, 2.2
MAP_BOX = (40, 330, W - 40, 1480)          # where the map sits on screen
PINK, TEAL, WHITE, MUTED = (255, 62, 165), (54, 241, 225), (246, 239, 250), (200, 185, 215)


def font(name, size):
    return ImageFont.truetype(FONT + name, size)


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ease(t):
    return 1 - (1 - t) ** 3


def background():
    bg = Image.new('RGB', (W, H))
    px = bg.load()
    for y in range(H):
        c = tuple(int(a + (b - a) * y / H) for a, b in zip((20, 8, 31), (44, 14, 66)))
        for x in range(W):
            px[x, y] = c
    return bg.convert('RGBA')


def fit_map(path):
    m = Image.open(path).convert('RGBA')
    bw, bh = MAP_BOX[2] - MAP_BOX[0], MAP_BOX[3] - MAP_BOX[1]
    s = min(bw / m.width, bh / m.height)
    m = m.resize((int(m.width * s), int(m.height * s)), Image.LANCZOS)
    ox = MAP_BOX[0] + (bw - m.width) // 2
    oy = MAP_BOX[1] + (bh - m.height) // 2
    return m, ox, oy


def polyline_upto(points, frac):
    """Points of the route drawn up to `frac` of its total length."""
    segs = [math.dist(points[i], points[i + 1]) for i in range(len(points) - 1)]
    total = sum(segs) or 1
    target, out = total * frac, [points[0]]
    for i, s in enumerate(segs):
        if target >= s:
            out.append(points[i + 1]); target -= s
        else:
            a, b = points[i], points[i + 1]
            r = target / s if s else 0
            out.append((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r))
            break
    return out


def host_badge(host):
    img = Image.open(os.path.join(ROOT, 'brand', f'crew-{host.lower()}.png')).convert('RGBA')
    size = 190
    side = min(img.size)
    img = img.crop(((img.width - side) // 2, 0, (img.width + side) // 2, side)).resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    badge = Image.new('RGBA', (size + 16, size + 16), (0, 0, 0, 0))
    ImageDraw.Draw(badge).ellipse([0, 0, size + 15, size + 15], fill=PINK + (255,))
    badge.paste(img, (8, 8), mask)
    return badge


def render(ep):
    routes = ep['routes']
    map_img, ox, oy = fit_map(os.path.join(ROOT, ep['map']) if not os.path.isabs(ep['map']) else ep['map'])
    base = background()
    base.alpha_composite(map_img, (ox, oy))
    d = ImageDraw.Draw(base)
    # title card
    tf = font('Inter-Black.otf', 70)
    title = ep['title']
    tw = d.textlength(title, font=tf)
    d.rounded_rectangle([(W - tw) / 2 - 34, 150, (W + tw) / 2 + 34, 262], 24, fill=(255, 255, 255, 240))
    d.text((W / 2, 206), title, font=tf, fill=(20, 8, 31), anchor='mm')
    badge = host_badge(ep['host'])
    pts = [[(ox + x * map_img.width, oy + y * map_img.height) for x, y in r['points']] for r in routes]

    dur = INTRO + PER_ROUTE * len(routes) + HOLD + END
    out = os.path.join(ROOT, ep['output']) if not os.path.isabs(ep['output']) else ep['output']
    os.makedirs(os.path.dirname(out), exist_ok=True)
    silent = out.replace('.mp4', '.silent.mp4')
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                           '-pix_fmt', 'yuv420p', silent], stdin=subprocess.PIPE)
    lab = font('Inter-Black.otf', 44); num = font('Inter-Black.otf', 76); small = font('Inter-ExtraBold.otf', 40)
    for n in range(int(dur * FPS)):
        t = n / FPS
        f = base.copy()
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        for i, r in enumerate(routes):
            start = INTRO + i * PER_ROUTE
            if t < start:
                continue
            p = min(1.0, (t - start) / (PER_ROUTE * 0.8))
            col = hex_rgb(r['color'])
            line = polyline_upto(pts[i], ease(p))
            if len(line) > 1:
                glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(glow).line(line, fill=col + (200,), width=26, joint='curve')
                layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
                ld.line(line, fill=col + (255,), width=10, joint='curve')
                hx, hy = line[-1]
                ld.ellipse([hx - 14, hy - 14, hx + 14, hy + 14], fill=WHITE + (255,), outline=col + (255,), width=6)
            # timer row
            y = 1520 + i * 105
            minutes = round(r['minutes'] * ease(p))
            ld.rounded_rectangle([60, y, W - 60, y + 90], 22, fill=(20, 8, 31, 215), outline=col + (255,), width=4)
            ld.text((100, y + 45), r['mode'], font=lab, fill=col + (255,), anchor='lm')
            ld.text((W - 100, y + 45), f'{minutes} MIN', font=num, fill=WHITE + (255,), anchor='rm')
        f.alpha_composite(layer)
        # host badge, intro only
        if t < INTRO + PER_ROUTE * len(routes) + HOLD:
            f.alpha_composite(badge, (50, 320))
            ImageDraw.Draw(f).text((50 + badge.width // 2, 320 + badge.height + 26), ep['host'].upper(), font=small, fill=WHITE, anchor='mm')
        # end card
        if t >= dur - END:
            a = min(1.0, (t - (dur - END)) / 0.3)
            ov = Image.new('RGBA', (W, H), (14, 6, 22, int(215 * a)))
            od = ImageDraw.Draw(ov)
            od.text((W / 2, 860), 'FULL CLEAR', font=font('Inter-Black.otf', 120), fill=PINK + (int(255 * a),), anchor='mm')
            od.text((W / 2, 990), '@fullclearmap', font=font('Inter-Black.otf', 70), fill=WHITE + (int(255 * a),), anchor='mm')
            od.text((W / 2, 1100), 'Full map & tracker · Link in bio', font=font('Inter-Black.otf', 52), fill=TEAL + (int(255 * a),), anchor='mm')
            f.alpha_composite(ov)
        ff.stdin.write(f.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()

    vo = ep.get('voiceover')
    if vo:
        vo = os.path.join(ROOT, vo) if not os.path.isabs(vo) else vo
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', silent, '-i', vo, '-filter_complex',
                        f'[1:a]apad,atrim=0:{dur},loudnorm=I=-14:TP=-1.5[a]', '-map', '0:v', '-map', '[a]',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', out], check=True)
    else:  # silent track so platforms accept it
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', silent, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                        '-shortest', '-c:v', 'copy', '-c:a', 'aac', '-movflags', '+faststart', out], check=True)
    os.remove(silent)
    print(f'{out}  ({dur:.1f}s)')


if __name__ == '__main__':
    render(json.load(open(sys.argv[1])))
