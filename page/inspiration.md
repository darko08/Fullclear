# Inspiration from the owner (ideas, not orders)

The owner sends examples of what other pages/creators do. They are **ideas to learn from, not things to copy**.
For each: what it is, what we take, what we don't (rules: no reposting others' content, no Rockstar content in AI tools, verified facts only).

| Date | What the owner sent | What we take | What we don't |
|---|---|---|---|
| 2026-11-18 | "Faceless GTA 6 Clipping Page: Setup Prompt" (2 pages) | Whole playbook structure: pillars, daily slots, credit/permission rules, launch-day playbook, learning loop, file structure → `page/playbook.md` | Buffer (we use Postiz); "official trailer clips" only trimmed + captioned, never AI-processed |
| 2026-11-18 | Video "Your GTA VI Mayor: how long it takes to cross Leonida" | Format "How long does it take…?" with routes + timers → our own series (`tools/route_video.py`, measured by us after launch) | Their video and map (not ours) |
| 2026-11-18 | Video "Bober smart: GTA 6 is about to create a new wave of internet millionaires" (an automated "launch cut pipeline": beat-synced vertical cuts with one/two-word giant captions like "VICE CITY", "LEONIDA", "THE CREW", "OUT NOV 19") | **Beat-synced hype edits**: fast cuts on the beat, one giant word per cut, 15–25 s. We can do this with official Rockstar "download and share" trailer footage: trim only (ffmpeg, no AI), our captions, trailer music muted → platform/licensed sound, "© Rockstar Games". Also shows an automated pipeline sells: ours already is one | Their clips; Rockstar music (Content ID) |
| 2026-11-18 | X article by @Richard_YTS (YouTube strategist) | Couldn't open (X login). Owner to send text/screenshot | — |
| 2026-11-18 | Ad: "GTA 6 Faceless Channel System" ($70 bundle: strategy, Claude skill that cuts trailers + voice + music, packaging, monetization, 100 ideas) | Confirms our direction. Ideas to apply ourselves: **packaging** (title + thumbnail tests, first-second hook), **long-form YouTube** (maps/secrets/stories explainers: Shorts alone grow slowly to monetization), 30-day plan structure | Not buying (we already have the pipeline; spending needs owner). Their skill feeds trailers into AI and adds music: against Rockstar ToS / Content ID risk for us |

## Ideas queue from inspiration
1. **Beat-cut hype shorts** from official trailers ("LEONIDA", "VICE CITY", "OUT NOW"): build `tools/beat_cut.py` (detect beats in a licensed/platform track, cut official clips on beats, giant captions).
2. ~~SSD install explainer~~ done: HOW TO #1 (tools/howto_short.py), scheduled Nov 19 15:00 UTC.
3. **Long-form YouTube (8–12 min)**: "Every region of Leonida explained", "All collectibles we know so far", built from official facts + our own map graphics + host. Needed for YouTube watch hours.
4. **Packaging tests**: two title/thumbnail variants per YouTube video (YouTube "Test & compare"), log the winner in learning.md.
