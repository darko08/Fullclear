# Full Clear Discord bot

Collects community clips with a licence agreement, runs a moderator review queue, awards points
and rank roles, and exports approved clips for the video editor.

| Command | Who | What |
|---|---|---|
| `/submit` | Everyone | Upload own clip/screenshot + category + location + description + consent |
| `/profile` | Everyone | Points, rank, approved finds |
| `/leaderboard` | Everyone | Top 10 contributors |
| `/export days:7` | Moderators | CSV of approved clips (file paths, credit names) for the editor |

Moderators review in **#clip-review** with **Approve**, **Approve + feature in video**, or **Reject** (asks
for a reason, which is DMed to the submitter). Clip files are downloaded to `data/clips/` at submit time
because Discord's attachment links expire.

## Setup (about 15 minutes)

1. Set up the server using [SERVER-BLUEPRINT.md](SERVER-BLUEPRINT.md).
2. Go to https://discord.com/developers/applications → **New Application** → name it *Full Clear*.
   * **Bot** tab → *Reset Token* → copy it (this is `DISCORD_TOKEN`; never share it).
   * **General Information** → copy *Application ID* (`CLIENT_ID`).
   * **OAuth2 → URL Generator** → scopes `bot` + `applications.commands`; bot permissions
     *Send Messages, Embed Links, Attach Files, Read Message History, Manage Roles* → open the URL → add to your server.
3. In Discord: User Settings → Advanced → **Developer Mode** on. Right-click to copy the server ID,
   `#clip-review` ID and `#community-finds` ID.
4. Drag the bot's role **above** Rookie/Pathfinder/Cartographer/Legend (Server Settings → Roles).
5. Install and run (Node.js 22.13+):

```bash
cp .env.example .env    # then fill in the values
```

```bash
npm install
```

```bash
npm run register
```

```bash
npm start
```

`npm test` runs the unit tests.

## Hosting

The bot must run 24/7. Cheapest options: a small VPS (Hetzner, DigitalOcean, ~$5/month) or Railway/Fly.io.
Keep the `data/` folder on persistent storage and back it up — it holds the database and all clips.
Once volume grows (hundreds of clips/week), move clip storage to Cloudflare R2 or S3.
