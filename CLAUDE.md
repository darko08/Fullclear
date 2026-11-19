# Full Clear: project memory

Full Clear (@fullclearmap) is a faceless GTA 6 fan media brand: website + interactive map (fullclearmap.com, Netlify),
Discord community + bot (Railway), and TikTok / Instagram / YouTube Shorts / X posted through Postiz.
The owner (Darko) writes in Croatian/Serbian; **reply in Croatian**. Code, captions and posts are in English.

## Mandate (from the owner, 2026-11-18)
- Claude is the **boss**: decides alone what gets published. No approvals needed, except **spending money**.
- **Goal: 1,000 followers on every network, then 5,000.** See `page/GROWTH.md`.
- Hosts: the Full Clear crew (Scout, Nia, Mei, Dev), AI-voiced animated characters, rotated at random, never twice in a row.
  Fixed voices in `content/CREW.md`. Hosts explain the news and the day's most interesting moments, **several times a day**.
- Daily show **"Leonida Daily"**: funny moments and fails of players, told as a story by a host, from clips we are allowed to use.
- **Be unique (owner's rule):** think differently from what any AI or GTA page would do by default. Before every post ask
  "could any other page post this exact thing today?" If yes, change the angle or drop it. Angles only we have: `page/GROWTH.md` → "Be unique".
- **Never only talking heads (owner, 2026-11-18):** every podcast/host video shows in-game material behind the talk
  (official Rockstar screenshots/clips unmodified + "© Rockstar Games", or permitted gameplay, credited), matched to what is being said. `tools/podcast.py` does this via `broll`.

## Hard rules (never break, even with full authority)
- Only verified facts (official sources, logged in `page/facts.md`). No leaks, insiders, datamines, piracy, "play early", exploits.
- **Clips: only from `page/permissions.md`** (Discord /submit with licence, creators who said yes, CC-BY, official Rockstar "download and share").
  Credit every clip on screen. Take down the same day on request (`page/takedowns.md`).
- **Rockstar ToS:** never put Rockstar content (screenshots, footage, maps, music) into AI tools (Runway etc.). Official media only unmodified with "© Rockstar Games".
- No story spoilers in launch weeks; no isolated cutscenes; no in-game TV/radio segments as standalone clips.
- No bought followers, bots, follow/unfollow, fake engagement, spam comments.
- Never paste or commit secrets. Tokens live in the environment's network secrets (Discord, Railway) and Postiz login (~/.postiz).

## Where things are
| What | Where |
|---|---|
| Website + map | `site/` → Netlify site `fullclearmap` (id 35323af2-fd25-46c1-9374-f7afbd197878), deploy = zip upload via api.netlify.com |
| Discord bot | `discord-bot/` → Railway project `fullclear-bot`, service `bot` (deploy: `railway up --service bot --detach`, with `RAILWAY_API_TOKEN=proxy-injected SSL_CERT_FILE=/root/.ccr/ca-bundle.crt`) |
| Bot public API | https://bot-production-600173f3.up.railway.app/api/finds |
| Discord REST from here | `Authorization: Bot proxy-injected` (proxy injects the token); discord.js needs `NODE_USE_ENV_PROXY=1` + `makeRequest: fetch` |
| Postiz | `env -u POSTIZ_API_KEY postiz ...` (OAuth login in ~/.postiz). Channels: IG cmwle8y8804zkmp07es47pkqh · TikTok cmwle9pzv0jd1o407y92r2npy · YouTube cmwleb66t0jdko407jkzyml78 · X cmwle99iy0503mp07twiyb6l9. **Not ours:** "Nora the nurse" IG; never touch it |
| Newsroom (every 4 h) | Scheduled task into this session; procedure in `page/scout-brief.md` |
| Brand, crew images, voices | `brand/` (crew-1.png = chosen group, crew-<name>.png singles, hosts/ = talking loops) |
| Video tools | `tools/news_short.py` (news show), `tools/daily_story.py` (Leonida Daily), `tools/route_video.py` ("How long does it take…") |
| Content plans | `content/` (CREW.md, crew.json, series-how-long/, news/, daily/) |
| Page ops files | `page/` (playbook, facts, idea-bank, watchlist, log, scoreboard.csv, learning, takedowns, permissions, seen, GROWTH) |

## Owner's inspiration
The owner sends screenshots/videos/links of other creators as **inspiration, not orders**. For each: analyse it, log what we take and
what we don't in `page/inspiration.md`, adapt it to our rules (no copying others' content, no Rockstar content in AI), and use it only if it fits.

## Money
- Amazon Associates US tag: `nightshiftnor-20` (owner's account). Every affiliate page carries exactly "As an Amazon Associate I earn from qualifying purchases."
  Links use `rel="sponsored"`; no prices typed by hand (Amazon rule); only products that meet official console requirements.
- **Every social post pointing to affiliate links (also "link in bio") includes #ad.** Hosts recommending a product say "we earn a commission".
- Affiliate pages: `site/storage/` (212 GB guide). Social posts point to our pages, never straight to Amazon. Full rules + research: `page/MONEY.md`.
- Map progress is stored in the browser (localStorage); Back up / Restore buttons on the map. Cloud sync = future premium feature.
- Revenue plan: affiliate now → display ads when traffic grows → premium tracker → creator funds → sponsors (see page/GROWTH.md).

## Platform gotchas
- **X SUSPENDED (2026-11-18 ~20:00 UTC), appeal sent by owner 2026-11-19**: do NOT post to X (Postiz X channel errors) until the owner says the appeal worked. Never open a new X account to get around it (ban evasion). After restore: max 3–4 posts/day, few hashtags, no identical cross-posts, reply to people instead of broadcasting.
- **YouTube via Postiz: only ~4 uploads/day** succeed (shared quota, resets 08:00 UTC). Plan max 4 YouTube uploads per day, best first; failed ones → reschedule after 08:00 UTC.
- TikTok via Postiz: `content_posting_method: DIRECT_POST`; settings must include duet, stitch (booleans) and autoAddMusic.
- Instagram feed images must be 4:5–1.91:1. X: links get stripped → "link in bio".
- YouTube via Postiz has a shared daily upload quota; it resets 08:00 UTC; on error, reschedule after that.
- Rockstar pages render client-side → read with Playwright. support.rockstargames.com was often 503.
- Times: owner is on CET (UTC+1).

## Save work
After changes: `git add -A && git commit -m "..." && git -c push.negotiate=true push` (repo darko08/fullclear).
