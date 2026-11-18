// Full Clear Discord bot: collects community clips, runs a moderator review queue,
// awards points and ranks, and exports approved clips for the video editor.
const fs = require('node:fs');
const path = require('node:path');
const { Readable } = require('node:stream');
const { pipeline } = require('node:stream/promises');
const {
  Client, GatewayIntentBits, Events, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle,
  ModalBuilder, TextInputBuilder, TextInputStyle, AttachmentBuilder, PermissionFlagsBits, MessageFlags,
} = require('discord.js');
const { env, POINTS, RANKS, LICENSE_TEXT } = require('./config');
const { openDb } = require('./db');
const { rankFor, validateSubmission, parseClipLink, safeFileName, toCsv } = require('./logic');

const TOKEN = env('DISCORD_TOKEN');
const REVIEW_CHANNEL_ID = env('REVIEW_CHANNEL_ID');   // private, moderators only
const FINDS_CHANNEL_ID = env('FINDS_CHANNEL_ID');     // public showcase of approved finds
const DATA_DIR = path.resolve(env('DATA_DIR', './data'));
const CLIPS_DIR = path.join(DATA_DIR, 'clips');
const SITE_URL = env('SITE_URL', 'https://fullclearmap.com');

fs.mkdirSync(CLIPS_DIR, { recursive: true });
const db = openDb(path.join(DATA_DIR, 'fullclear.db'));

// Extra intents only when Scout AI is on (they must be enabled for the app in the Developer Portal).
const AI_ON = Boolean(process.env.ANTHROPIC_API_KEY);
const client = new Client({ intents: [
  GatewayIntentBits.Guilds,
  ...(AI_ON ? [GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent, GatewayIntentBits.GuildMembers] : []),
] });
require('./community').setupCommunity(client, db);
const EPHEMERAL = { flags: MessageFlags.Ephemeral };

client.once(Events.ClientReady, (c) => console.log(`Full Clear bot online as ${c.user.tag}`));

client.on(Events.InteractionCreate, async (i) => {
  try {
    if (i.isChatInputCommand()) {
      if (i.commandName === 'submit') return await handleSubmit(i);
      if (i.commandName === 'profile') return await handleProfile(i);
      if (i.commandName === 'leaderboard') return await handleLeaderboard(i);
      if (i.commandName === 'export') return await handleExport(i);
      if (i.commandName === 'setpin') return await handleSetPin(i);
    }
    if (i.isButton() && i.customId.startsWith('review:')) return await handleReviewButton(i);
    if (i.isModalSubmit() && i.customId.startsWith('reject:')) return await handleRejectModal(i);
  } catch (err) {
    console.error(err);
    const msg = { content: 'Something went wrong. The team has been notified.', ...EPHEMERAL };
    if (i.deferred || i.replied) await i.followUp(msg).catch(() => {});
    else if (i.isRepliable()) await i.reply(msg).catch(() => {});
  }
});

async function handleSubmit(i) {
  const clip = i.options.getAttachment('clip');
  const link = i.options.getString('link');
  const error = validateSubmission({
    consent: i.options.getBoolean('consent', true),
    contentType: clip ? clip.contentType : undefined,
    sizeBytes: clip ? clip.size : undefined,
    link,
    submittedToday: db.pendingToday(i.user.id),
  });
  if (error) return i.reply({ content: `❌ ${error}\n\n**Licence:** ${LICENSE_TEXT}`, ...EPHEMERAL });

  await i.deferReply(EPHEMERAL);
  const sourceUrl = clip ? clip.url : parseClipLink(link);

  const id = db.addSubmission({
    userId: i.user.id,
    userTag: i.user.username,
    category: i.options.getString('category', true),
    location: i.options.getString('location', true),
    description: i.options.getString('description', true),
    creditName: i.options.getString('credit') || i.user.username,
    sourceUrl,
  });

  if (clip) {
    // Discord CDN links expire, so keep our own copy immediately.
    const fileName = safeFileName(id, clip.name);
    const filePath = path.join(CLIPS_DIR, fileName);
    const res = await fetch(clip.url);
    if (!res.ok) throw new Error(`Download failed for submission ${id}: ${res.status}`);
    await pipeline(Readable.fromWeb(res.body), fs.createWriteStream(filePath));
    db.raw.prepare('UPDATE submissions SET file_path = ? WHERE id = ?').run(filePath, id);
  }

  const s = db.getSubmission(id);
  const review = await client.channels.fetch(REVIEW_CHANNEL_ID);
  await review.send({
    content: `New submission #${id} from <@${i.user.id}>${clip ? '' : ' (🔗 link, not a file: the editor downloads it from the creator\'s own upload)'}\n${sourceUrl}`,
    embeds: [submissionEmbed(s, 0xf5a623)],
    components: [reviewButtons(id)],
  });

  await i.editReply(`✅ Got it! Submission **#${id}** is in the review queue. ` +
    `You'll get a DM when it's approved (+${POINTS.approved} points, more if we feature it in a video).`);
}

function submissionEmbed(s, color) {
  return new EmbedBuilder()
    .setColor(color)
    .setTitle(`#${s.id} · ${s.category}`)
    .addFields(
      { name: 'Location', value: s.location },
      { name: 'Description', value: s.description },
      { name: 'Credit as', value: s.credit_name, inline: true },
      { name: 'Status', value: s.status, inline: true },
    )
    .setTimestamp(new Date(`${s.created_at}Z`));
}

function reviewButtons(id) {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder().setCustomId(`review:approve:${id}`).setLabel('Approve').setStyle(ButtonStyle.Success),
    new ButtonBuilder().setCustomId(`review:feature:${id}`).setLabel('Approve + feature in video').setStyle(ButtonStyle.Primary),
    new ButtonBuilder().setCustomId(`review:reject:${id}`).setLabel('Reject').setStyle(ButtonStyle.Danger),
  );
}

function isModerator(i) {
  return i.memberPermissions?.has(PermissionFlagsBits.ManageMessages);
}

async function handleReviewButton(i) {
  if (!isModerator(i)) return i.reply({ content: 'Moderators only.', ...EPHEMERAL });
  const [, action, idStr] = i.customId.split(':');
  const id = Number(idStr);

  if (action === 'reject') {
    const modal = new ModalBuilder().setCustomId(`reject:${id}`).setTitle(`Reject #${id}`).addComponents(
      new ActionRowBuilder().addComponents(
        new TextInputBuilder().setCustomId('reason').setLabel('Reason (sent to the submitter)')
          .setStyle(TextInputStyle.Short).setMaxLength(200).setRequired(true)
          .setPlaceholder('Duplicate / not your own clip / wrong location / low quality'),
      ),
    );
    return i.showModal(modal);
  }

  if (!db.review(id, 'approved', i.user.id)) {
    return i.reply({ content: `#${id} was already reviewed.`, ...EPHEMERAL });
  }
  const featured = action === 'feature';
  const s = db.getSubmission(id);
  const earned = POINTS.approved + (featured ? POINTS.featured : 0);
  const total = db.addPoints(s.user_id, s.user_tag, earned);

  await i.update({
    content: `${i.message.content}\n**${featured ? 'Approved + featured' : 'Approved'}** by <@${i.user.id}>`,
    embeds: [submissionEmbed(s, 0x2ecc71)],
    components: [],
  });

  const finds = await client.channels.fetch(FINDS_CHANNEL_ID);
  await finds.send({
    content: `📍 **New community find** by <@${s.user_id}>${featured ? ' · 🎬 coming to our videos!' : ''}\n${s.source_url}`,
    embeds: [submissionEmbed(s, 0x2ecc71).setFooter({ text: `Full map: ${SITE_URL}` })],
  });

  const rankUp = await syncRank(i.guild, s.user_id, total);
  await dm(s.user_id,
    `🎉 Your submission **#${id}** was approved! +${earned} points (total **${total}**).` +
    (featured ? '\n🎬 It will be featured in a Full Clear video with credit to **' + s.credit_name + '**.' : '') +
    (rankUp ? `\n⬆️ You ranked up to **${rankUp}**!` : ''));
}

async function handleRejectModal(i) {
  if (!isModerator(i)) return i.reply({ content: 'Moderators only.', ...EPHEMERAL });
  const id = Number(i.customId.split(':')[1]);
  const reason = i.fields.getTextInputValue('reason');
  if (!db.review(id, 'rejected', i.user.id, reason)) {
    return i.reply({ content: `#${id} was already reviewed.`, ...EPHEMERAL });
  }
  const s = db.getSubmission(id);
  if (s.file_path) fs.rm(s.file_path, { force: true }, () => {});
  await i.update({
    content: `${i.message.content}\n**Rejected** by <@${i.user.id}>: ${reason}`,
    embeds: [submissionEmbed(s, 0xe74c3c)],
    components: [],
  });
  await dm(s.user_id, `Your submission **#${id}** wasn't approved: ${reason}\nNo worries, keep hunting!`);
}

// Gives the member the role for their current rank and removes lower rank roles.
// Returns the new rank name if it changed.
async function syncRank(guild, userId, points) {
  if (!guild) return null;
  const member = await guild.members.fetch(userId).catch(() => null);
  if (!member) return null;
  const { current } = rankFor(points);
  const target = guild.roles.cache.find((r) => r.name === current.role);
  if (!target || member.roles.cache.has(target.id)) return null;
  const others = RANKS.map((r) => guild.roles.cache.find((x) => x.name === r.role))
    .filter((r) => r && r.id !== target.id && member.roles.cache.has(r.id));
  await member.roles.add(target).catch((e) => console.warn('Role add failed (check role order):', e.message));
  if (others.length) await member.roles.remove(others).catch(() => {});
  return current.role;
}

async function dm(userId, content) {
  const user = await client.users.fetch(userId).catch(() => null);
  await user?.send(content).catch(() => {}); // users may have DMs closed
}

async function handleProfile(i) {
  const points = db.getPoints(i.user.id);
  const { current, next } = rankFor(points);
  const embed = new EmbedBuilder().setColor(0x1abc9c).setTitle(`${i.user.username} · ${current.role}`)
    .addFields(
      { name: 'Points', value: String(points), inline: true },
      { name: 'Approved finds', value: String(db.countByUser(i.user.id, 'approved')), inline: true },
      { name: 'Next rank', value: next ? `${next.role} at ${next.points} pts` : 'Max rank 👑', inline: true },
    );
  return i.reply({ embeds: [embed], ...EPHEMERAL });
}

async function handleLeaderboard(i) {
  const rows = db.leaderboard(10);
  const medals = ['🥇', '🥈', '🥉'];
  const text = rows.length
    ? rows.map((r, n) => `${medals[n] ?? `**${n + 1}.**`} <@${r.user_id}> · ${r.total} pts`).join('\n')
    : 'No approved finds yet. Be the first with `/submit`!';
  return i.reply({
    embeds: [new EmbedBuilder().setColor(0xf1c40f).setTitle('🏆 Top Scouts').setDescription(text)],
    allowedMentions: { parse: [] },
  });
}

async function handleExport(i) {
  if (!isModerator(i)) return i.reply({ content: 'Moderators only.', ...EPHEMERAL });
  const days = i.options.getInteger('days') ?? 7;
  const since = new Date(Date.now() - days * 864e5).toISOString().replace('T', ' ').slice(0, 19);
  const rows = db.approvedSince(since);
  const file = new AttachmentBuilder(Buffer.from(toCsv(rows)), { name: `approved-clips-${days}d.csv` });
  return i.reply({ content: `${rows.length} approved clips in the last ${days} days. Files are in \`${CLIPS_DIR}\`.`, files: [file], ...EPHEMERAL });
}

async function handleSetPin(i) {
  if (!isModerator(i)) return i.reply({ content: 'Moderators only.', ...EPHEMERAL });
  const id = i.options.getInteger('id', true);
  const x = i.options.getNumber('x', true);
  const y = i.options.getNumber('y', true);
  const ok = db.setPin(id, x, y);
  return i.reply({ content: ok ? `📍 #${id} is now on the map at (${x}, ${y}): ${SITE_URL}/map` : `#${id} isn't an approved submission.`, ...EPHEMERAL });
}

require('./api').startApi(db);
client.login(TOKEN);
