# Full Clear Discord — server blueprint

Goal: turn TikTok/Instagram viewers into Discord members, and members into clip contributors.
The loop: **video → Discord → `/submit` clip → approved → featured in next video with credit → more people join.**

## 1. Create the server (10 minutes)

1. Discord → **+** → *Create My Own* → *For a club or community*. Name: **Full Clear**. Icon: chosen Scout design.
2. Server Settings → **Enable Community** (gives you Onboarding, Rules screening, Announcement channels).
3. Server Settings → **Safety Setup**: verification level *Medium*, AutoMod on (spam, mention spam, keyword filter for "mod menu", "money drop", "recovery", "free download").

## 2. Roles (create in this order, top to bottom)

| Role | Who | Notes |
|---|---|---|
| **Admin** | You | All permissions |
| **Moderator** | Trusted helpers | *Manage Messages* — this is what lets them use review buttons and `/export` |
| **Full Clear Bot** | The bot | Must sit **above** the rank roles or it can't assign them |
| **Legend** | 300+ pts | Gold, displayed separately |
| **Cartographer** | 100+ pts | Purple, displayed separately |
| **Pathfinder** | 30+ pts | Teal |
| **Rookie** | 0+ pts | Grey |
| **Creator** | Partner streamers/YouTubers | Given by hand |
| **Supporter** | Premium subscribers (later) | |

## 3. Channels

```
📌 START HERE
  #welcome            – read-only: what Full Clear is, how to earn ranks
  #rules              – read-only: rules + CLIP LICENCE (text below)
  #announcements      – new videos, new map categories, giveaways

🎬 SUBMIT & SHOWCASE
  #how-to-submit      – read-only: pinned guide to /submit with example
  #submit-here        – only place /submit works best (slow mode 30s)
  #community-finds    – bot posts approved finds here (read-only for members)
  #featured-in-videos – links to videos that used member clips (shout-outs)

🗺️ THE HUNT
  #collectibles   #hidden-locations   #easter-eggs
  #money-methods  #vehicles-and-weapons   #help-where-is-it

💬 COMMUNITY
  #general   #screenshots   #funny-moments   #find-a-crew (for Online later)

🔒 STAFF (Moderators only)
  #clip-review     – bot posts every submission here with Approve / Feature / Reject buttons
  #mod-chat
```

## 4. Text for #rules (copy-paste)

> **Full Clear rules**
> 1. Be decent. No harassment, slurs or spam.
> 2. **No cheats, mod menus, money drops, account selling or "recovery" services.** Instant ban.
> 3. No leaks or piracy links.
> 4. Spoilers go in spoiler tags `||like this||` for the first 4 weeks after launch.
> 5. **Only submit clips you recorded yourself.** Reposting someone else's clip = ban.
>
> **Clip licence** — by using `/submit` you confirm you recorded the clip yourself, and you give
> Full Clear a non-exclusive, worldwide, royalty-free licence to edit and publish it on our website and
> social channels, with credit to the name you choose. You keep ownership. Ask a moderator any time
> and we'll stop using it in new content.
>
> Full Clear is a fan community and is not affiliated with or endorsed by Rockstar Games or Take-Two Interactive.

## 5. Text for #how-to-submit (copy-paste)

> **Earn points & get featured** 🎬
> 1. Record the find on PS5 (Create button → *Save recent gameplay*) or Xbox (Xbox button → *Capture*).
> 2. Send it to your phone (PS App / Xbox App) — keep it **under 60 seconds**.
> 3. In #submit-here type `/submit`, attach the clip, pick the category, write where it is.
> 4. Set `consent` to **True** (it's your own clip — see #rules).
>
> ✅ Approved = **+10 pts** · 🎬 Featured in a video = **+25 pts** and your name on screen
> Ranks: Rookie → Pathfinder (30) → Cartographer (100) → Legend (300)
> `/profile` shows your points · `/leaderboard` shows the top Scouts

## 6. Onboarding (Server Settings → Onboarding)

Question: *"What are you hunting?"* → Collectibles / Easter eggs / Money / Crew for Online.
Each answer opens the matching channel and gives a role, so members land somewhere relevant
instead of a wall of channels.

## 7. Growing it from TikTok / Instagram

* **Invite link:** Server → Invite → *Edit invite link* → never expires, unlimited uses.
  Create **one invite per platform** (TikTok, Instagram, YouTube) — Server Settings → Invites shows
  how many joined through each, so you know which platform works.
* **Every video ends with:** *"Found something? Send it in — link in bio — you could be in the next video."*
* **Bio link:** one link page (fullclearmap.com, see `/site`) with the Discord button on top.
* **Credit on screen** ("Found by @name") in every video that uses a member clip, then post the video in
  #featured-in-videos and tag them. This is the single strongest reason people submit.
* **Weekly "Top Scout"** shout-out video from the `/leaderboard`.
* Giveaways: stick to non-cash prizes you own (premium months, merch later) and post simple
  written rules; cash/console giveaways have legal requirements by country.

## 8. Daily routine (15–30 min)

1. Open #clip-review → Approve / Feature / Reject each submission.
2. `/export days:1` → send the CSV + clip files to the editor.
3. Drop the day's videos in #announcements.
