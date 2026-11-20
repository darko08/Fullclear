#!/usr/bin/env python3
"""Daily wide CC BY sweep (YouTube Data API, ≤6 searches, last 24 h, sorted by views). Writes /tmp/lv/sweep.json; owner downloads picks to Drive."""
import os; os.makedirs("/tmp/lv", exist_ok=True)
import json, re, urllib.parse, urllib.request, datetime as dt, sys
sys.path.insert(0,'tools'); import clip_hunter as ch
API='https://www.googleapis.com/youtube/v3/'
def get(path, **p):
    with urllib.request.urlopen(API+path+'?'+urllib.parse.urlencode(p), timeout=30) as r: return json.load(r)
since=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')
Q=['GTA 6 gameplay no commentary','GTA 6 funny moments','GTA 6 what happens if','GTA 6 location guide','GTA 6 easter egg','GTA 6 stunt']  # max 6 searches (100 units each)
ids={}
for q in Q:
    for it in get('search',part='id',q=q,type='video',videoLicense='creativeCommon',order='viewCount',publishedAfter=since,maxResults=25).get('items',[]):
        ids.setdefault(it['id']['videoId'],q)
seen=json.load(open('page/clip-hunt-state.json'))
rows=[]
L=list(ids)
for k in range(0,len(L),50):
    for v in get('videos',part='snippet,status,contentDetails,statistics',id=','.join(L[k:k+50])).get('items',[]):
        s=v['snippet']
        if v['status'].get('license')!='creativeCommon' or s.get('liveBroadcastContent')!='none': continue
        if ch.BLOCK_CH.search(s['channelTitle']) or ch.BLOCK_TITLE.search(s['title']): continue
        if 'gta' not in (s['title']+s.get('description','')).lower(): continue
        m=re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',v['contentDetails']['duration']); secs=sum(int(x or 0)*f for x,f in zip(m.groups(),(3600,60,1)))
        if secs<20: continue
        rows.append(dict(id=v['id'],t=s['title'],c=s['channelTitle'],cid=s['channelId'],secs=secs,views=int(v['statistics'].get('viewCount',0)),q=ids[v['id']],seen=v['id'] in seen,thumb=s['thumbnails'].get('high',s['thumbnails']['default'])['url']))
rows.sort(key=lambda r:-r['views'])
json.dump(rows,open('/tmp/lv/sweep.json','w'),indent=1)
for i,r in enumerate(rows): print(i,r['id'],r['views'],f"{r['secs']//60}:{r['secs']%60:02d}",r['c'][:22],'|',r['t'][:75],'| seen' if r['seen'] else '')
