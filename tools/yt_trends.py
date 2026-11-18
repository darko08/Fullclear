#!/usr/bin/env python3
"""YouTube trend scout: which GTA 6 videos are winning right now, and which are "outliers"
(many more views than the channel has subscribers = the topic/hook won, not the channel size).

Uses the YouTube Data API v3 (key is injected by the environment proxy for www.googleapis.com; never stored here).
Quota: each search = 100 units, videos/channels = 1 unit per call (daily limit 10,000).

Usage: python3 tools/yt_trends.py [--hours 24] [--query "GTA 6"] [--out page/yt-trends.md]
"""
import argparse, datetime as dt, json, re, urllib.parse, urllib.request

API = 'https://www.googleapis.com/youtube/v3/'


def get(path, **params):
    url = API + path + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def secs(iso):
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or '')
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=int, default=24)
    ap.add_argument('--query', default='GTA 6')
    ap.add_argument('--out', default='page/yt-trends.md')
    ap.add_argument('--cc', action='store_true', help='only Creative Commons videos (clip candidates)')
    a = ap.parse_args()
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=a.hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
    ids = []
    for dur in ('short', 'medium'):   # short = under 4 min (Shorts live here), medium = 4-20 min
        r = get('search', part='id', q=a.query, type='video', order='viewCount', publishedAfter=since,
                videoDuration=dur, maxResults=50, relevanceLanguage='en', **({'videoLicense': 'creativeCommon'} if a.cc else {}))
        ids += [i['id']['videoId'] for i in r.get('items', [])]
    vids = []
    for k in range(0, len(ids), 50):
        r = get('videos', part='snippet,statistics,contentDetails,status', id=','.join(ids[k:k + 50]))
        vids += r.get('items', [])
    chans = {}
    cids = list({v['snippet']['channelId'] for v in vids})
    for k in range(0, len(cids), 50):
        r = get('channels', part='statistics', id=','.join(cids[k:k + 50]))
        chans.update({c['id']: int(c['statistics'].get('subscriberCount', 0) or 0) for c in r.get('items', [])})
    rows = []
    for v in vids:
        s, st = v['snippet'], v['statistics']
        views = int(st.get('viewCount', 0)); subs = chans.get(s['channelId'], 0)
        rows.append(dict(id=v['id'], title=s['title'], channel=s['channelTitle'], views=views, likes=int(st.get('likes', st.get('likeCount', 0)) or 0),
                         comments=int(st.get('commentCount', 0) or 0), subs=subs, ratio=views / max(subs, 100), secs=secs(v.get('contentDetails', {}).get('duration')),
                         cc=v['status'].get('license') == 'creativeCommon', published=s['publishedAt']))
    rows.sort(key=lambda r: -r['views'])
    out = [f"# YouTube trends: \"{a.query}\", last {a.hours} h (generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC)\n",
           "Views/subs ratio > 3 = outlier (the topic won, not the channel). CC = Creative Commons licence (candidate for our clips, check for overlays).\n",
           "## Top by views\n", "| Views | Ratio | Len | Title | Channel | CC |", "|---:|---:|---:|---|---|---|"]
    for r in rows[:25]:
        out.append(f"| {r['views']:,} | {r['ratio']:.1f} | {r['secs']}s | [{r['title'][:80]}](https://youtu.be/{r['id']}) | {r['channel']} | {'CC' if r['cc'] else ''} |")
    out += ["\n## Outliers (ratio > 3, at least 5,000 views)\n", "| Views | Subs | Ratio | Len | Title | Channel |", "|---:|---:|---:|---:|---|---|"]
    for r in sorted([r for r in rows if r['ratio'] > 3 and r['views'] >= 5000], key=lambda r: -r['ratio'])[:20]:
        out.append(f"| {r['views']:,} | {r['subs']:,} | {r['ratio']:.1f} | {r['secs']}s | [{r['title'][:80]}](https://youtu.be/{r['id']}) | {r['channel']} |")
    shorts = [r for r in rows if r['secs'] <= 180]
    if shorts:
        out.append(f"\nShorts (≤180 s) in sample: {len(shorts)}, median views {sorted(x['views'] for x in shorts)[len(shorts) // 2]:,}. "
                   f"Long (>180 s): {len(rows) - len(shorts)}.")
    out.append("\n## CC BY candidates (check permissions.md rules: own footage, no webcam/stream overlays)\n")
    for r in [r for r in rows if r['cc']][:15]:
        out.append(f"- {r['views']:,} views · [{r['title'][:80]}](https://youtu.be/{r['id']}) · {r['channel']}")
    open(a.out, 'w').write('\n'.join(out) + '\n')
    json.dump(rows, open(a.out.replace('.md', '.json'), 'w'), indent=1)
    print(f'{len(rows)} videos -> {a.out}')


if __name__ == '__main__':
    main()
