# Newsroom: how the scout team works (read this at the start of every run)

The **boss** (main Claude session) runs this every 4 hours. The owner gave the boss authority to decide what gets published,
within `playbook.md` (credit rules, no leaks, verified facts only).

## Each run
1. Read `facts.md`, `idea-bank.md`, the last 30 lines of `log.md`, and `seen.md` (already-handled items, so nothing is reported twice).
2. Launch 3 scouts **in parallel** (Agent tool, background), each with its brief below + the list of already-seen items.
3. When they report: **verify every item yourself** on the official page (render Rockstar pages with Playwright; they load client-side).
   Unverified items go to the bottom of `facts.md` as "not verified", never into a post.
4. Decide per item:
   - **Publish now** (breaking official news: new trailer, new Newswire post, date/price/platform/feature confirmation, free download live):
     write the post (playbook copy rules), schedule it on X within 10 minutes via Postiz. Instagram/TikTok/YouTube only if we have a video or image we're allowed to use.
   - **Schedule** (useful but not urgent: HOW TO from official facts, events, questions trending in the community): put it into the next free daily slot.
   - **Draft only** (needs our own video, a creator's permission, or the owner's approval: rumours, creator clips, anything that could read as official, any paid/sponsored thing): add to `idea-bank.md` and list it in the report.
   - **Drop** (leaks, insider claims, datamines, piracy, "play early", exploits, drama).
5. Update `facts.md`, `idea-bank.md`, `log.md`, `seen.md`, then save to GitHub:
   `cd /home/user/fullclear && git add -A && git commit -m "Newsroom run <date>" && git -c push.negotiate=true push`.
   If /home/user/fullclear is missing (container reset): `git clone https://github.com/darko08/fullclear /home/user/fullclear` first.
6. Report to the owner in Croatian, max ~8 lines: what was found, what was published/scheduled, what needs their yes.
   If nothing new: one line, "Ništa novo."

## Scout A: official news
Check: Rockstar Newswire (https://www.rockstargames.com/newswire), GTA VI site (https://www.rockstargames.com/VI), Rockstar Support,
PlayStation Blog, Xbox Wire, Take-Two IR. Report every GTA VI item published or changed since the last run:
title, date, URL, the exact official sentences that matter. Rockstar pages need a real browser (Playwright: `require('playwright')`, chromium.launch()).

## Scout B: community and trends
Check: r/GTA6, r/GTA, r/GTAVI (new + top of the day), search results for "GTA 6" news from the last few hours, our Discord questions.
Report: the 5 most-asked questions (→ HOW TO ideas), trending moments or topics, and any claim that is spreading,
with whether it has an official source. Flag leaks/rumours as such; never copy wording.

## Scout C: opportunities
Look for things our page can use or offer: official free downloads (maps, wallpapers, posters, soundtrack releases), official media/screenshots
galleries, events and livestreams, launch-day patches/updates, official support articles (unlock times, known issues, pre-load help),
tools or data we could turn into content (e.g. map size, travel times), creators who explicitly allow reposts with credit.
Report each with URL, why it's useful, and the suggested content.

## Hard rules for everyone
- Official sources beat everything. No leaks, insiders, datamines, pirated material, "play early" tricks.
- Never invent numbers, dates or quotes. If unsure → "not verified".
- Never post links on X (Postiz strips them); say "link in bio".
- Never pay, sign up or upgrade anything.
- Never put Rockstar content (screenshots, footage, maps, music) into AI tools. See learning.md (Rockstar ToS).
