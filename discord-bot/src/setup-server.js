// One-shot server builder: creates roles, categories, channels, permissions, info messages and
// per-platform invites on the server the bot was added to. Safe to re-run (skips what exists).
// Uses only the REST API. Run: npm run setup-server
const fs = require('node:fs');
const path = require('node:path');
const { REST, Routes, ChannelType, PermissionFlagsBits: P } = require('discord.js');
const { RANKS, LICENSE_TEXT, POINTS } = require('./config');

const token = process.env.DISCORD_TOKEN || 'placeholder-injected-by-proxy';
// Use Node's global fetch so HTTPS_PROXY is respected when NODE_USE_ENV_PROXY=1.
const rest = new REST({ makeRequest: (url, init) => fetch(url, init) }).setToken(token);
const SITE = process.env.SITE_URL || 'https://fullclearmap.com';

const ROLE_SPECS = [
  { name: 'Moderator', color: 0xff3ea5, hoist: true,
    permissions: P.ManageMessages | P.KickMembers | P.ModerateMembers | P.ViewChannel | P.SendMessages | P.ReadMessageHistory },
  { name: 'Creator', color: 0xff9f1c, hoist: true },
  { name: 'Supporter', color: 0x36f1e1, hoist: false },
  { name: 'Legend', color: 0xffd166, hoist: true },
  { name: 'Cartographer', color: 0xb88cff, hoist: true },
  { name: 'Pathfinder', color: 0x36f1e1, hoist: false },
  { name: 'Rookie', color: 0x9e8fb0, hoist: false },
];

// readonly: members can read but not post. staff: only Moderators can see. slow: slowmode seconds.
const LAYOUT = [
  { category: '📌 START HERE', channels: [
    { name: 'welcome', readonly: true, topic: 'What Full Clear is and how to get featured' },
    { name: 'rules', readonly: true, topic: 'Rules + clip licence' },
    { name: 'announcements', readonly: true, topic: 'New videos, map updates' },
  ] },
  { category: '🎬 SUBMIT & SHOWCASE', channels: [
    { name: 'how-to-submit', readonly: true, topic: 'How /submit works' },
    { name: 'submit-here', slow: 30, topic: 'Use /submit here: your own clips only' },
    { name: 'community-finds', readonly: true, topic: 'Approved finds from the community' },
    { name: 'featured-in-videos', readonly: true, topic: 'Videos that used member clips' },
  ] },
  { category: '🗺️ THE HUNT', channels: [
    { name: 'collectibles' }, { name: 'hidden-locations' }, { name: 'easter-eggs' },
    { name: 'money-methods' }, { name: 'vehicles-and-weapons' }, { name: 'help-where-is-it' },
  ] },
  { category: '💬 COMMUNITY', channels: [
    { name: 'general' }, { name: 'screenshots' }, { name: 'funny-moments' }, { name: 'find-a-crew' },
  ] },
  { category: '🔒 STAFF', staff: true, channels: [
    { name: 'clip-review', topic: 'Bot posts every submission here' }, { name: 'mod-chat' }, { name: 'mod-log' },
  ] },
];

const MESSAGES = {
  welcome: [
    `# Welcome to Full Clear 🎯\n**Find everything. Miss nothing.**\n\nWe're mapping every collectible, easter egg and secret in GTA 6, together. ` +
    `The best finds go in our TikTok, Instagram & YouTube videos **with your name on screen**.\n\n` +
    `**Start here:**\n1️⃣ Read <#rules>\n2️⃣ Learn how to send clips in <#how-to-submit>\n3️⃣ Post your finds in <#submit-here> with \`/submit\`\n\n` +
    `🗺️ Map & tracker: ${SITE}\n\n*Fan community, not affiliated with Rockstar Games or Take-Two Interactive.*`,
  ],
  rules: [
    `# Rules\n1. Be decent. No harassment, slurs or spam.\n` +
    `2. **No cheats, mod menus, money drops, account selling or "recovery" services.** Instant ban.\n` +
    `3. No leaks or piracy links.\n4. Spoilers in spoiler tags \`||like this||\` for the first 4 weeks.\n` +
    `5. **Only submit clips you recorded yourself.** Reposting someone else's clip = ban.\n` +
    `6. Nobody from staff will ever DM you asking for logins or payment.`,
    `# Clip licence\n${LICENSE_TEXT}\n\nYou keep ownership. Ask a Moderator any time and we'll stop using it in new content.`,
  ],
  'how-to-submit': [
    `# Earn points & get featured 🎬\n` +
    `1. Record the find. **PS5:** Create button → *Save recent gameplay*. **Xbox:** Xbox button → *Capture*.\n` +
    `2. Send it to your phone with the PlayStation App or Xbox App. Keep it **under 60 seconds**.\n` +
    `3. In <#submit-here> type \`/submit\`, attach the clip, pick the category, write where it is.\n` +
    `4. Set \`consent\` to **True** (it's your own clip, see <#rules>).\n\n` +
    `✅ Approved = **+${POINTS.approved} pts**  ·  🎬 Featured in a video = **+${POINTS.featured} more** and your name on screen\n` +
    `**Ranks:** ${RANKS.map((r) => r.points ? `${r.role} (${r.points})` : r.role).join(' → ')}\n` +
    `\`/profile\` your points  ·  \`/leaderboard\` top Scouts`,
  ],
};

const INVITES = ['tiktok', 'instagram', 'youtube', 'website'];

async function main() {
  const me = await rest.get(Routes.user());
  const guilds = await rest.get(Routes.userGuilds());
  if (guilds.length !== 1) throw new Error(`Bot must be in exactly one server, found ${guilds.length}. Set GUILD_ID to choose.`);
  const guildId = process.env.GUILD_ID || guilds[0].id;
  console.log(`Bot ${me.username} → server "${guilds[0].name}" (${guildId})`);

  // Roles
  const roles = await rest.get(Routes.guildRoles(guildId));
  const everyone = roles.find((r) => r.id === guildId);
  const roleId = {};
  for (const spec of ROLE_SPECS) {
    let r = roles.find((x) => x.name === spec.name);
    if (!r) {
      r = await rest.post(Routes.guildRoles(guildId), { body: {
        name: spec.name, color: spec.color, hoist: spec.hoist, mentionable: false,
        permissions: String(spec.permissions ?? everyone.permissions),
      } });
      console.log(`  + role ${spec.name}`);
    }
    roleId[spec.name] = r.id;
  }
  // Order: our roles just below the bot's own role, in ROLE_SPECS order.
  const all = await rest.get(Routes.guildRoles(guildId));
  const botRole = all.find((r) => r.tags?.bot_id === me.id);
  if (botRole) {
    const top = botRole.position - 1;
    await rest.patch(Routes.guildRoles(guildId), { body: ROLE_SPECS.map((s, i) => ({ id: roleId[s.name], position: Math.max(1, top - i) })) })
      .catch((e) => console.warn('  ! could not reorder roles:', e.message));
  }

  // Channels
  const existing = await rest.get(Routes.guildChannels(guildId));
  const chan = {};
  const VIEW = P.ViewChannel;
  for (const group of LAYOUT) {
    let cat = existing.find((c) => c.type === ChannelType.GuildCategory && c.name === group.category);
    const catOverwrites = group.staff ? [
      { id: guildId, type: 0, deny: String(VIEW) },
      { id: roleId.Moderator, type: 0, allow: String(VIEW | P.SendMessages | P.ReadMessageHistory) },
      { id: me.id, type: 1, allow: String(VIEW | P.SendMessages | P.EmbedLinks | P.ReadMessageHistory) },
    ] : [];
    if (!cat) {
      cat = await rest.post(Routes.guildChannels(guildId), { body: { name: group.category, type: ChannelType.GuildCategory, permission_overwrites: catOverwrites } });
      console.log(`  + category ${group.category}`);
    }
    for (const c of group.channels) {
      let ch = existing.find((x) => x.name === c.name && x.parent_id === cat.id);
      if (!ch) {
        const overwrites = [...catOverwrites];
        if (c.readonly) overwrites.push(
          { id: guildId, type: 0, deny: String(P.SendMessages | P.CreatePublicThreads | P.CreatePrivateThreads) },
          { id: roleId.Moderator, type: 0, allow: String(P.SendMessages) },
          { id: me.id, type: 1, allow: String(P.SendMessages | P.EmbedLinks | P.AttachFiles) },
        );
        ch = await rest.post(Routes.guildChannels(guildId), { body: {
          name: c.name, type: c.type ?? ChannelType.GuildText, parent_id: cat.id, topic: c.topic,
          rate_limit_per_user: c.slow, permission_overwrites: overwrites,
        } });
        console.log(`    + #${c.name}`);
      }
      chan[c.name] = ch.id;
    }
  }

  // Info messages (only into empty channels, so re-runs don't duplicate)
  for (const [name, msgs] of Object.entries(MESSAGES)) {
    const last = await rest.get(Routes.channelMessages(chan[name]), { query: new URLSearchParams({ limit: '1' }) });
    if (last.length) continue;
    for (const content of msgs) await rest.post(Routes.channelMessages(chan[name]), { body: { content, allowed_mentions: { parse: [] } } });
    console.log(`  + messages in #${name}`);
  }

  // Server settings: Community mode (rules screen, announcements), safety
  await rest.patch(Routes.guild(guildId), { body: {
    verification_level: 2, explicit_content_filter: 2, default_message_notifications: 1,
    features: [...new Set([...(await rest.get(Routes.guild(guildId))).features, 'COMMUNITY'])],
    rules_channel_id: chan.rules, public_updates_channel_id: chan['mod-log'], system_channel_id: chan.general,
    description: 'The community hunting every collectible, easter egg and secret in GTA 6.',
  } }).then(() => console.log('  ✓ community mode + safety settings'))
    .then(() => rest.patch(Routes.channel(chan.announcements), { body: { type: ChannelType.GuildAnnouncement } })
      .then(() => console.log('  ✓ #announcements is now an announcement channel'))
      .catch((e) => console.warn('  ! could not convert #announcements:', e.message)))
    .catch((e) => console.warn('  ! community mode not enabled (do it by hand in Server Settings → Enable Community):', e.message));

  // Permanent invites, one per platform (Server Settings → Invites shows joins per link)
  // Discord invites can't carry a label, so we keep a local map label → code.
  const invites = {};
  const current = await rest.get(Routes.guildInvites(guildId));
  const mapFile = path.resolve(process.env.DATA_DIR || './data', 'invites.json');
  let saved = {}; try { saved = JSON.parse(fs.readFileSync(mapFile, 'utf8')); } catch {}
  for (const label of INVITES) {
    if (saved[label] && current.some((i) => i.code === saved[label])) { invites[label] = saved[label]; continue; }
    const inv = await rest.post(Routes.channelInvites(chan.welcome), { body: { max_age: 0, max_uses: 0, unique: true } });
    invites[label] = inv.code;
  }
  fs.mkdirSync(path.dirname(mapFile), { recursive: true });
  fs.writeFileSync(mapFile, JSON.stringify(invites, null, 2));

  const out = { CLIENT_ID: me.id, GUILD_ID: guildId, REVIEW_CHANNEL_ID: chan['clip-review'], FINDS_CHANNEL_ID: chan['community-finds'] };
  console.log('\nInvites:'); for (const [k, v] of Object.entries(invites)) console.log(`  ${k.padEnd(10)} https://discord.gg/${v}`);
  console.log('\nFor .env:'); for (const [k, v] of Object.entries(out)) console.log(`${k}=${v}`);
  fs.writeFileSync(path.resolve(process.env.DATA_DIR || './data', 'server-ids.json'), JSON.stringify({ ...out, invites }, null, 2));
}

main().catch((e) => { console.error('Setup failed:', e.rawError ?? e.message); process.exit(1); });
