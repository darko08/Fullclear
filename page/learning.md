# Learning

## Current rules
- Hosts speak calm and confident; shouting tags make the voice raspy (2026-11-18).
- Never repost other creators' videos without their yes (2026-11-18).

## Wins
## Losses
- Robot mascot rejected by owner → replaced by the 4-person crew (2026-11-18).

## Early lessons to TEST (from the setup prompt, not proven for us)
- Official trailer clips beat text-only posts.
- Countdown posts are reliable.
- Credited creator clips and HOW TO posts pull saves and shares.

## Rules added 2026-11-18 (scout run 1)
- Rockstar reportedly takes down story-spoiler videos → we never post story content in launch week; gameplay/driving/map/NPC only.
- Never promote "switch region to play early" tricks (not confirmed, possible account risk).
- Reddit blocks automated reading; scouts rely on news coverage of threads → always open the original before crediting.

## Legal rules from Rockstar ToS (scout C, 2026-11-18). These are binding for us
- ToS §2.3: never feed Rockstar screenshots, footage, music, characters or maps into AI tools (Runway etc.). Our crew and scenes stay 100% original prompts.
  → Our own map must NOT be made by AI from the official map. Link to Rockstar's official map download; don't rehost it.
- Official media ("download and share") may be shown unmodified with "© Rockstar Games" credit.
- Fan-video policy (support page, unverified text): non-commercial fan use tolerated; no story spoilers, isolated cutscenes, in-game TV/radio segments, leaks, cheat promotion.
- Monetisation with Rockstar footage is a grey area → our money should come from our own content (crew videos, map/tracker data, community), not from Rockstar footage.
- Briefs must state times correctly: NZ unlock = 11:00 UTC Nov 18 (scout B corrected the boss). Anything 'NZ gameplay' before that is fake/leak.
- YouTube rate-limits this machine (429) on watch pages after a few runs → space out scout D checks; tonight's Leonida Daily may need the host-only fallback.

## 2026-11-18 18:00 UTC: YouTube trends (tools/yt_trends.py, last 24 h, 100 GTA 6 videos)
- **Relatable POV/skit Shorts win launch eve** (17–38 s): "Players before GTA 6 releases", "Never call in sick for GTA 6", "The night of GTA 6", "When GTA 6 finally drops" (1.5–2.4M). → our crew/Keys & Neon can do short relatable bits with official screens.
- **Region-timing questions are big outliers:** "Mexico will be the last country to play GTA 6" (1.2M, 31× subs). → "Where does it unlock last?" only with verified local-midnight facts (PS Blog: each country at its midnight).
- **"Day 1 checklist"** = outlier (13.9×). → Morning Drive Nov 19 = our verified Day 1 checklist (update 14.23, 212 GB, unlock, map tracker).
- **Psychology/"the truth" angle** ("GTA 6 is changing your brain", 6.9×). **Long info dumps** still pull (11–15 min, 0.25–1.1M) → weekly podcast with B-roll.
- Avoid: "NZ trick" content (outlier, but promotes a region workaround → our no-"play early" rule).
- Shorts median views in top-100 sample: ~443k; half of the top 100 are long videos/streams.
- **Instagram rejects 96 kHz audio** ("could not process the media"): Leonida Daily #1 and podcast renders had 96 kHz (loudnorm upsamples). Fixed: all tools now force `-ar 48000`; re-posted IG.

## 2026-11-18 end of day 1
- **X account suspended** (~20:00 UTC). Likely cause: brand-new account + ~16 scheduled automated posts on day 1 + many hashtags + same text style → spam/automation filter. Lesson: new accounts warm up slowly (2–3 posts/day week 1, replies and real interaction, no bursts). Appeal by the owner.
- **YouTube: only 4 of 11 uploads went through** (Postiz shared daily quota). Lesson: max 4 YouTube uploads/day, prioritise long-form podcast + best Shorts.
- **Instagram rejects 96 kHz audio** (fixed in tools).
- Numbers day 1 (23:30 UTC): YouTube 4 Shorts, 99 views total (Metascore 99: 46, PS5 update: 37, fake downloads: 16, pre-orders: 0), 0 subs. TikTok platform views 4 (analytics lag). IG reach 17 (analytics lag, data to Nov 17).

## 2026-11-19 18:00 UTC: day 1 vs day 0
- Instagram is our only network with real reach: platform views 774, reach 671 (day 0: 17). Best = practical/useful (212 GB 126, fake downloads 111) and Leonida Daily #1 (116). Keys & Neon #1 (5) and the podcast clip (22) underperform → fewer talking-head formats on IG, more useful/funny gameplay.
- TikTok: every post 0–2 views → posts are very likely private/under review (unaudited API posting or new-account restriction). Owner to check in the TikTok app.
- YouTube: 197 views total on 8 Shorts (day 0: 99), 0 subscribers; news Shorts with a number in the title win (Metascore 99: 58).
- Discord: 4 members, no /submit yet → need invites in every caption/bio and a reason to join (map pins with names).
- 2026-11-20 00:56 UTC: YouTube Data API 'Search Queries per day' quota hit (wide 12-query sweep + scouts + clip hunter). Searches cost 100 units; keep sweeps to ≤6 queries; quota resets 08:00 UTC.
- Brand: never use official shots Vice_City_06 (police + bikinis) or Vice_City_07 (strip club) as B-roll (no sexualized imagery).

## 2026-11-20: never resend clip links (owner)
I sent the same YouTube links twice (scout D list in the newsroom report, then again merged into the clip-hunt list). Fix: every link list goes through `tools/clip_hunter.py --filter <ids>` (skips already-sent + already-on-Drive, then marks them). clip_hunter also skips ids already on Drive.
