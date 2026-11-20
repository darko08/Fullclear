#!/usr/bin/env python3
"""Clip hunter: find NEW Creative Commons (CC BY) GTA VI gameplay videos for Leonida Daily / Discord / B-roll.

YouTube Data API (key injected by the proxy for www.googleapis.com). Owner downloads the picks to the shared Drive
(YouTube blocks our server); tools/check_drive.py then picks them up.

Usage: python3 tools/clip_hunter.py [--hours 3] [--max 8]
Writes page/clip-hunt.md (latest list) + a thumbnail contact sheet for the boss to check webcams/overlays:
/tmp/clip-hunt-thumbs.jpg. State of already-proposed ids: page/clip-hunt-state.json.
Ranking: trusted own-gameplay channels first, then new channels; skips blocklisted channels and risky titles.
"""
import argparse, datetime as dt, io, json, os, re, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://www.googleapis.com/youtube/v3/'
STATE = os.path.join(ROOT, 'page/clip-hunt-state.json')
OUT = os.path.join(ROOT, 'page/clip-hunt.md')
TRUSTED = {'UCmF3ZcCBFUD-mcwg-r3SMyA': 'LunarGaming', 'UC20VvWjAyaGERxHwFGqN0_w': 'Soiscool Mec', 'UCLlka7pcpir-5koCjX1jLRw': 'Nippton Games'}
# guide channels with CC BY GTA VI uploads (own gameplay + voice; use muted as B-roll / how-to, credit on screen). Added 2026-11-20 after 6+ CC BY guides.
GUIDES = {'DPJ', 'LunarGaming', 'Vandal'}
BLOCK_CH = re.compile(r'H4Community|Gosoi|RJME|CalMarTV|Clips?\b|Reelity|Grand Theft Auto Clips|Viral|Highlights|Moments 24|Compil|GOAT361|Steezy|Muvee|Ducky|Vice City Brief|GamesWayFirst|reaction|ZeNoX|How to Everything|CHOWH1|TbOne|Lambret77|Darius2L|WNK GTA|Aidko|greey_mx|mr_gta|Witalo Games|Higor-BMX|Anjaan clipper|GowthMode|SPEED6ix|Gods of Garena|LIGHTNING SHORTS|MutatedWorm|Tomatolist|Jervin|Sagar Strike|PriAg|Trickmaster714|Fire wolf Gamer|BornInGame|Knights of Gaming|Mateo Roblox|ChrisReloads|Just Ganesh|gta2k26|Hantar_FF|Cheezy|Adriel P|Tinted|PS5 GPT|VexVice|GTA 6 Locker|ImCallvinn|BoltBrain|Mythic Realm', re.I)
BLOCK_TITLE = re.compile(r'twitch|mrbeast|nolan|review|lucia|jason|glitch|money glitch|exploit|early access|play early|leak|nude|strip|xqc|kai cenat|speed|caseoh|stream|live|mission \d|walkthrough|ending|chapter|mod\b|gta 5|gta v\b|free download|pc download', re.I)
FUN = re.compile(r'fail|funny|chaos|wtf|crash|ragdoll|police|cops|stars|what happens|tried|steal|escape|chase|insane|lol|wasted|busted|physics|npc', re.I)
QUERIES = ['GTA 6 funny', 'GTA 6 fail', 'GTA 6 what happens if', 'GTA 6 guide location', 'GTA 6 gameplay no commentary']  # 100 quota units each; 3 channels + 5 queries = 800 units × 8 runs/day (daily limit 10,000 incl. trends + scouts)


def get(path, **p):
    with urllib.request.urlopen(API + path + '?' + urllib.parse.urlencode(p), timeout=30) as r:
        return json.load(r)


def main():
    a = argparse.ArgumentParser(); a.add_argument('--hours', type=int, default=3); a.add_argument('--max', type=int, default=8); a = a.parse_args()
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=a.hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
    seen = json.load(open(STATE)) if os.path.exists(STATE) else {}
    ids = set()
    for ch in TRUSTED:   # 100 units each
        for it in get('search', part='id', channelId=ch, type='video', order='date', publishedAfter=since, maxResults=15).get('items', []):
            ids.add(it['id']['videoId'])
    for q in QUERIES:
        for it in get('search', part='id', q=q, type='video', videoLicense='creativeCommon', order='date', publishedAfter=since, maxResults=25).get('items', []):
            ids.add(it['id']['videoId'])
    ids -= set(seen)
    rows = []
    for k in range(0, len(ids), 50):
        chunk = list(ids)[k:k + 50]
        for v in get('videos', part='snippet,status,contentDetails,statistics', id=','.join(chunk)).get('items', []):
            s = v['snippet']; t = s['title']; ch = s['channelTitle']
            if v['status'].get('license') != 'creativeCommon': continue
            if s.get('liveBroadcastContent') != 'none' or not v.get('contentDetails', {}).get('duration'): continue
            if BLOCK_CH.search(ch) or BLOCK_TITLE.search(t): continue
            if 'gta' not in (t + ' ' + s.get('description', '')).lower(): continue
            m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', v['contentDetails']['duration']); secs = sum(int(x or 0) * f for x, f in zip(m.groups(), (3600, 60, 1)))
            if secs < 15 or secs > 900: continue
            fun = bool(FUN.search(t))
            guide = ch in GUIDES or re.search(r'how to|location|guide|no commentary|free roam', t, re.I)
            if not fun and not guide: continue   # fun → Leonida Daily; guides/no-commentary → long videos + Discord how-tos
            score = (2 if s['channelId'] in TRUSTED or ch in GUIDES else 0) + (3 if fun else 2) + min(2, int(v['statistics'].get('viewCount', 0) or 0) // 5000)
            rows.append(dict(id=v['id'], title=t, channel=ch, trusted=s['channelId'] in TRUSTED, secs=secs, score=score,
                             views=int(v['statistics'].get('viewCount', 0) or 0), thumb=s['thumbnails'].get('high', s['thumbnails']['default'])['url']))
    rows.sort(key=lambda r: -r['score']); rows = rows[:a.max]
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M')
    lines = [f'# Clip hunt {now} UTC (CC BY, last {a.hours} h)\n', 'Owner: download these to the shared Drive (keep the [id] in the file name).\n']
    for r in rows:
        lines.append(f"- {'⭐' if r['trusted'] else '🆕'} https://www.youtube.com/watch?v={r['id']} · {r['title'][:80]} · {r['channel']} · {r['secs']//60}:{r['secs']%60:02d} · {r['views']:,} views")
        seen[r['id']] = now
    if not rows: lines.append('No new CC BY candidates.')
    open(OUT, 'w').write('\n'.join(lines) + '\n'); json.dump(seen, open(STATE, 'w'), indent=1)
    # thumbnails for webcam / overlay check
    try:
        from PIL import Image, ImageDraw
        ims = []
        for r in rows:
            with urllib.request.urlopen(r['thumb'], timeout=20) as f: im = Image.open(io.BytesIO(f.read())).convert('RGB').resize((320, 180))
            ImageDraw.Draw(im).text((4, 4), r['id'], fill='yellow'); ims.append(im)
        if ims:
            sheet = Image.new('RGB', (320 * min(4, len(ims)), 180 * ((len(ims) + 3) // 4)))
            for i, im in enumerate(ims): sheet.paste(im, ((i % 4) * 320, (i // 4) * 180))
            sheet.save('/tmp/clip-hunt-thumbs.jpg')
    except Exception as e:
        print('thumbs failed:', e)
    print('\n'.join(lines))


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise SystemExit('YouTube API quota used up for today (resets 08:00 UTC). No clip hunt this run.')
        raise
