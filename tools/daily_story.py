#!/usr/bin/env python3
"""Full Clear "LEONIDA DAILY": a daily story compilation of players' funny moments and fails.

ONLY use clips listed in page/permissions.md (Discord /submit, creators who said yes, CC-BY, official Rockstar clips).
Every clip gets an on-screen credit for its whole duration.

Usage:  python3 tools/daily_story.py content/daily/<day>.json
{
  "host": "Mei",
  "title": "LEONIDA DAILY #1",
  "hook": "Day 1 in Leonida went… badly",
  "clips": [
    {"file": "page/media/raw/clip1.mp4", "start": 3.0, "end": 9.5,
     "credit": "@creator", "line": "Chapter 1: the parking job"},
    ...
  ],
  "voiceover": "videos/daily/day1-vo.mp3",   # the host narrates the story over the clips
  "clip_volume": 0.35,                        # original clip audio under the narration
  "output": "videos/daily/leonida-daily-01.mp4"
}
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont
from brand import SHOW_HOSTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = '/usr/share/fonts/opentype/inter/'
W, H, FPS = 1080, 1920, 30
INTRO, OUTRO = 1.6, 2.2
PINK, TEAL, WHITE, MUTED = (255, 62, 165), (54, 241, 225), (246, 239, 250), (200, 185, 215)


def p(x):
    return x if os.path.isabs(x) else os.path.join(ROOT, x)


def font(n, s):
    return ImageFont.truetype(F + n, s)


def run(cmd):
    subprocess.run(cmd, check=True)


def card(path, draw_fn):
    img = Image.new('RGB', (W, H))
    px = img.load()
    for y in range(H):
        c = tuple(int(a + (b - a) * y / H) for a, b in zip((20, 8, 31), (50, 14, 72)))
        for x in range(W):
            px[x, y] = c
    img = img.convert('RGBA')
    draw_fn(img, ImageDraw.Draw(img))
    img.convert('RGB').save(path)


def still_video(png, seconds, out):
    run(['ffmpeg', '-loglevel', 'error', '-y', '-loop', '1', '-i', png, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
         '-t', str(seconds), '-r', str(FPS), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-shortest', out])


def overlay_png(text_top, credit, out_png):
    """Transparent overlay: story line at top, credit at bottom."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    tf = font('Inter-Black.otf', 62)
    words, lines, cur = text_top.upper().split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=tf) <= W - 140: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    y = 170
    for line in lines:
        tw = d.textlength(line, font=tf)
        d.rounded_rectangle([(W - tw) / 2 - 24, y - 8, (W + tw) / 2 + 24, y + 74], 16, fill=(255, 255, 255, 235))
        d.text((W / 2, y + 33), line, font=tf, fill=(20, 8, 31), anchor='mm'); y += 92
    cf = font('Inter-Black.otf', 48)
    label = f'🎥 {credit}'.replace('🎥 ', 'CLIP: ')
    tw = d.textlength(label, font=cf)
    d.rounded_rectangle([(W - tw) / 2 - 26, H - 300, (W + tw) / 2 + 26, H - 220], 20, fill=PINK + (240,))
    d.text((W / 2, H - 260), label, font=cf, fill=WHITE, anchor='mm')
    img.save(out_png)


def render(ep):
    tmp = tempfile.mkdtemp()
    parts = []
    host = Image.open(p(f"brand/crew-{ep['host'].lower()}.png")).convert('RGBA').resize((520, 520), Image.LANCZOS)

    def intro(img, d):
        if SHOW_HOSTS: img.alpha_composite(host, ((W - 520) // 2, 520))
        else: d.text((W / 2, 760), f"told by {ep['host']}", font=font('Inter-Black.otf', 54), fill=TEAL, anchor='mm')
        d.rounded_rectangle([W / 2 - 250, 230, W / 2 + 250, 310], 20, fill=PINK)
        d.text((W / 2, 270), ep.get('title', 'LEONIDA DAILY'), font=font('Inter-Black.otf', 46), fill=WHITE, anchor='mm')
        hf = font('Inter-Black.otf', 70); y = 1120
        words, cur, lines = ep['hook'].upper().split(), '', []
        for w in words:
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=hf) <= W - 120: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        for line in lines:
            d.text((W / 2, y), line, font=hf, fill=WHITE, anchor='mm'); y += 86
    card(f'{tmp}/intro.png', intro); still_video(f'{tmp}/intro.png', INTRO, f'{tmp}/00_intro.mp4'); parts.append(f'{tmp}/00_intro.mp4')

    for i, c in enumerate(ep['clips']):
        overlay_png(c.get('line', ''), c['credit'], f'{tmp}/ov{i}.png')
        dur = c['end'] - c['start']
        # 9:16: blurred fill behind, the clip itself fitted to the width
        fc = (f"[0:v]trim={c['start']}:{c['end']},setpts=PTS-STARTPTS,fps={FPS},split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:5[bg];"
              f"[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v0];[v0][1:v]overlay=0:0,format=yuv420p[v];"
              f"[0:a]atrim={c['start']}:{c['end']},asetpts=PTS-STARTPTS,aresample=48000,volume={ep.get('clip_volume', 0.35)}[a]")
        out = f'{tmp}/{i + 1:02d}.mp4'
        has_audio = bool(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', p(c['file'])],
                                        capture_output=True, text=True).stdout.strip())
        extra = []
        if not has_audio:  # silent clip: feed a silent track as input 2
            extra = ['-f', 'lavfi', '-t', str(c['end'] + 1), '-i', 'anullsrc=r=48000:cl=stereo']
            fc = fc.replace(f"[0:a]atrim={c['start']}:{c['end']},asetpts=PTS-STARTPTS", f"[2:a]atrim=0:{dur},asetpts=PTS-STARTPTS")
        run(['ffmpeg', '-loglevel', 'error', '-y', '-i', p(c['file']), '-i', f'{tmp}/ov{i}.png', *extra, '-filter_complex', fc,
             '-map', '[v]', '-map', '[a]', '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-c:a', 'aac', '-ar', '48000', out])
        parts.append(out)

    def outro(img, d):
        d.text((W / 2, 820), 'FULL CLEAR', font=font('Inter-Black.otf', 120), fill=PINK, anchor='mm')
        d.text((W / 2, 950), '@fullclearmap', font=font('Inter-Black.otf', 70), fill=WHITE, anchor='mm')
        d.text((W / 2, 1060), 'Got a funnier clip? Send it in', font=font('Inter-Black.otf', 52), fill=TEAL, anchor='mm')
        d.text((W / 2, 1140), 'Discord · link in bio', font=font('Inter-Black.otf', 52), fill=TEAL, anchor='mm')
        credits = 'Clips: ' + ', '.join(dict.fromkeys(c['credit'] for c in ep['clips']))
        d.text((W / 2, 1320), credits, font=font('Inter-SemiBold.otf', 34), fill=MUTED, anchor='mm')
    card(f'{tmp}/outro.png', outro); still_video(f'{tmp}/outro.png', OUTRO, f'{tmp}/99_outro.mp4'); parts.append(f'{tmp}/99_outro.mp4')

    with open(f'{tmp}/list.txt', 'w') as fh:
        fh.writelines(f"file '{x}'\n" for x in parts)
    run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{tmp}/list.txt', '-c:v', 'libx264', '-preset', 'medium',
         '-crf', '20', '-c:a', 'aac', '-ar', '48000', f'{tmp}/joined.mp4'])
    out = p(ep['output']); os.makedirs(os.path.dirname(out), exist_ok=True)
    vo = ep.get('voiceover')
    if vo:  # narration starts after the intro card, clip audio stays underneath
        run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'{tmp}/joined.mp4', '-i', p(vo), '-filter_complex',
             f'[1:a]adelay={int(INTRO * 1000)}|{int(INTRO * 1000)},volume=1.0[n];[0:a][n]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]',
             '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', out])
    else:
        run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'{tmp}/joined.mp4', '-c', 'copy', '-movflags', '+faststart', out])
    print(out)


if __name__ == '__main__':
    render(json.load(open(sys.argv[1])))
