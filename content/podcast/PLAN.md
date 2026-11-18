# "Leonida After Hours": the Full Clear podcast (plan, 2026-11-18)

Owner's order (2026-11-18): a podcast about the game, with topics, guests and events. Claude is the **video + audio editor**;
scouts constantly hunt for news and stories before anyone else.

Why it's ours (the "be unique" test): GTA 6 itself introduced on-demand podcasts for the first time (PS Blog, Nov 18).
Our show feels like a podcast *from* Leonida, hosted by four characters who have a life of their own: their rivalry, running jokes, their own "map pins".
Nobody else has a crew; everybody else has one faceless narrator.

## 1. Formats
| Show | Length | When | What |
|---|---|---|---|
| **Morning Drive** (daily) | 3–5 min | Every day 07:30 CET (06:30 UTC), before US wakes up | 2 hosts. Overnight news (verified), the best community find, one question for the day. |
| **Leonida After Hours** (weekly) | 20–30 min | Sunday 20:00 CET | All 4 hosts. Segments below. The main episode. |
| **Breaking** (when needed) | 1–2 min | Within the hour of big official news | 1–2 hosts. Patch, outage, free download, announcement. |
| **Clips** | 30–60 s | 3 per episode | Best moments cut vertically → TikTok/IG/Shorts/X, "full episode: link in bio". |

## 1b. "Keys & Neon" (owner's idea, 2026-11-18): two AI characters debate and recap, 60–90 s
- **Rosa** (retired Florida Keys fishing-boat captain, 60s, deadpan sceptic; voice Mabel) vs **Jay** (Vice City nightlife creator, 20s, all hype; voice Malachi).
  Our own fictional characters (brand/guests/), always labelled "our own AI characters"; never real people, never Rockstar characters.
- Format: Jay brings the news/hype, Rosa undercuts it; every fact has a source on screen; ends with "Team Keys or Team Neon?".
- Topics: daily recap, pros vs cons of reviews, myth or fact (e.g. viral cheat lists that contradict each other), real Florida vs Leonida.
- Tool: `python3 tools/podcast.py content/podcast/knNN-*.json --clip 1 <last>` (vertical). Cadence: daily in launch weeks (evening US time).

## 2. Segments (pick 4–6 per weekly episode)
1. **Breaking Leonida**: verified news of the week, with source on screen (facts.md only).
2. **Found By…**: community finds from Discord /submit, finder credited by name (they share it → new listeners).
3. **Myth or Fact**: a claim spreading online; we say what's verified, what isn't. Never repeat leaks as fact.
4. **Crew Debate**: one hot take, two hosts on each side ("Vice City vs. the Keys", "best first car", "is 30 fps a problem?"). Fans vote in a poll, the result opens the next episode.
5. **Ask the Crew**: listener questions from comments/Discord (named with permission).
6. **Leonida Daily Replay**: the week's funniest permitted clips described (credited).
7. **Don't Buy This**: honest buying advice (affiliate only where genuinely useful; host says "we earn a commission"; #ad on posts).
8. **Records Board**: fastest, highest, longest: community/speedrun records with proof links.
9. **Podcast Review**: we review the *in-game* podcasts and radio as critics (talk about them; never play Rockstar audio as standalone segments, never put it into AI tools).
10. **Crew Lore**: 60 seconds of the crew's own running story (Dev's pin collection, Mei's binocular sightings, Nia's map, Scout's camera).

## 3. Guests
| Guest type | How | Rules |
|---|---|---|
| **Our crew** (Scout, Nia, Mei, Dev) | Rotating host + co-host every episode | Fixed voices (CREW.md). |
| **Discord members** | Record a voice question/answer in Discord or send a voice memo; sign the consent line in /submit or a form | Their real voice, with written consent; first name/handle only; no minors' personal info. |
| **Creators** (clippers, speedrunners, streamers) | DM template in permissions.md; 10-min recorded call or written Q&A read by a host ("Dev reads your answers") | Their real voice or a host reading their written answers, **clearly labelled**. Never an AI voice imitating a real person. |
| **Experts** (game journalists, Florida locals, car/boat people, map makers) | Written Q&A or recorded call | Same as creators. Great for "Real Florida vs. Leonida". |
| **"Guest from Leonida"** (fictional character of ours, e.g. a grumpy Keys fishing guide) | Our own character, own AI voice | Clearly a fictional character of ours; never a Rockstar character, never a real person. |

Guest pipeline: Scout E (story hunter) proposes 3 guests a week → owner or Claude sends the invite (Claude only from our own accounts, never spam, max 5 invites/day) → log in `content/podcast/guests.md`.

## 4. Events calendar (verified dates only; check facts.md before each)
| Date | Event | Episode idea |
|---|---|---|
| Nov 19 | Launch + album (Rockstar) | Breaking: "It's out. What to do in the first hour" |
| Nov 19 (announced) | Official Leonida map download | Breaking + "our tracker vs. the official map" |
| Nov 22 (Sun) | First weekly episode | "Launch weekend: what we found" |
| Nov 27 | Black Friday | "Don't Buy This: Black Friday edition" (#ad) |
| Dec 11 | Original Score by Justice (Rockstar Newswire Oct 29) | Score review episode |
| First patch (TBA) | Patch notes | Breaking within the hour |
| Late Dec | End of year | "Leonida Awards" voted by Discord |
Unconfirmed events (online mode, DLC, Game Awards results) only after an official source.

## 5. Production pipeline (Claude = editor)
1. **Rundown** (`content/podcast/<id>.json`): segments, lines per host, sources per fact.
2. **Script rules:** each line ≤ 2 sentences, natural back-and-forth, one host ends each segment with a question for the audience. Same voice rules as CREW.md (no [laughs], no shouting).
3. **Voices:** one Runway speech call per line (eleven_v4, fixed voices) → `videos/podcast/<id>/NN-host.mp3`.
4. **Edit:** `tools/podcast.py` stitches lines with natural gaps, adds our own intro sting + music bed (Runway generate_music, our own, never Rockstar music), loudness -16 LUFS (podcast) / -14 (social).
5. **Video:** 16:9 "studio" with the 4 crew portraits, the speaker lights up and talks (host loops), subtitles, segment cards, sources on screen → YouTube full episode.
6. **Clips:** 3 vertical 9:16 cuts of the best moments → TikTok/IG/Shorts/X.
7. **Distribution (owner, 2026-11-18): YouTube only for now** (full episodes) + clips on TikTok/IG/Shorts/X. Spotify/Apple later, only if full-episode listening proves demand. Note: our podcast is *about* the game; it cannot be inside GTA (in-game podcasts are Rockstar's; no console mods).
8. **Log** in `page/log.md`; numbers in `scoreboard.csv`; learnings in `learning.md`.

## 6. Scouts for the podcast (see page/scout-brief.md)
- **Scout E: story hunter** (new): human stories, records, weird discoveries, creator feats, guest candidates, Florida-vs-Leonida parallels. Runs with every newsroom.
- Scouts A–D feed Breaking Leonida, Myth or Fact, Leonida Daily Replay.
- Rapid alert (hourly) → Breaking episodes.

## 7. First 6 episodes
| # | Show | Topic |
|---|---|---|
| 0 | Pilot (Nov 18) ✅ published 18:40 UTC | "Meet the crew" + GTA's first in-game podcasts + launch timing |
| 1 | Morning Drive Nov 19 | It's out: first-hour checklist, PS5 update 14.23, 212 GB |
| 2 | Morning Drive Nov 20 | First community finds, first myths |
| 3 | Weekly Nov 22 | Launch weekend: finds, debate "best region", Ask the Crew |
| 4 | Morning Drive | Map download, how our tracker works |
| 5 | Weekly Nov 29 | Black Friday: Don't Buy This (#ad), records board |

## 8. Hard rules (same as everywhere)
Verified facts only (facts.md) · no leaks/datamines/insiders · no story spoilers in launch weeks (spoiler warning + chapter marker if ever needed after) ·
no Rockstar audio/footage as standalone segments or in AI tools · real people only with consent and in their own voice · #ad + "we earn a commission" for affiliate mentions.
