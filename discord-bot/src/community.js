// Scout as community manager: welcomes new members, answers when talked to,
// posts a daily discussion prompt and a weekly leaderboard shout-out.
const { Events, ChannelType } = require('discord.js');

const ACTIVE_CHANNELS = ['help-where-is-it'];        // Scout answers every message here
const GENERAL = 'general';
const LAUNCH = Date.UTC(2026, 10, 19);
const USER_COOLDOWN_MS = 15_000;
const DAILY_LIMIT = Number(process.env.SCOUT_DAILY_LIMIT || 300); // cost guard
const TOPIC_HOUR_UTC = Number(process.env.DAILY_TOPIC_HOUR_UTC || 17);

function setupCommunity(client, db) {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.log('Scout AI is off: set ANTHROPIC_API_KEY to enable welcomes, replies and daily topics.');
    return;
  }
  const ai = require('./scout-ai');
  console.log(`Scout AI on (model ${ai.MODEL}, daily limit ${DAILY_LIMIT})`);

  const lastReply = new Map();

  function underDailyLimit() {
    const day = new Date().toISOString().slice(0, 10);
    const key = `ai-count:${day}`;
    const n = Number(db.getKv(key) || 0);
    if (n >= DAILY_LIMIT) return false;
    db.setKv(key, n + 1);
    return true;
  }

  const channelByName = (guild, name) =>
    guild.channels.cache.find((c) => c.type === ChannelType.GuildText && c.name === name);

  // 1) Welcome new members in #general
  client.on(Events.GuildMemberAdd, async (member) => {
    try {
      if (member.user.bot || !underDailyLimit()) return;
      const general = channelByName(member.guild, GENERAL);
      if (!general) return;
      const text = await ai.welcome({ memberName: member.displayName, memberCount: member.guild.memberCount });
      if (!text) return;
      const content = text.includes('{MENTION}') ? text.replaceAll('{MENTION}', `<@${member.id}>`) : `<@${member.id}> ${text}`;
      await general.send({ content, allowedMentions: { users: [member.id] } });
    } catch (e) { console.error('welcome failed:', e.message); }
  });

  // 2) Answer when mentioned, when someone replies to Scout, or anything in #help-where-is-it
  client.on(Events.MessageCreate, async (msg) => {
    try {
      if (msg.author.bot || !msg.guild || !msg.content?.trim()) return;
      const mentioned = msg.mentions.users.has(client.user.id);
      let repliedToScout = false;
      if (msg.reference?.messageId) {
        const ref = await msg.fetchReference().catch(() => null);
        repliedToScout = ref?.author?.id === client.user.id;
      }
      const inActive = ACTIVE_CHANNELS.includes(msg.channel.name);
      if (!mentioned && !repliedToScout && !inActive) return;

      const now = Date.now();
      if (now - (lastReply.get(msg.author.id) || 0) < USER_COOLDOWN_MS) return;
      if (!underDailyLimit()) return;
      lastReply.set(msg.author.id, now);

      await msg.channel.sendTyping().catch(() => {});
      const recent = await msg.channel.messages.fetch({ limit: 12, before: msg.id }).catch(() => null);
      const history = recent ? [...recent.values()].reverse()
        .filter((m) => m.content?.trim())
        .map((m) => ({ author: m.author.id === client.user.id ? 'Scout' : m.member?.displayName || m.author.username,
          content: m.cleanContent.slice(0, 400) })) : [];

      const text = await ai.replyTo({
        channelName: msg.channel.name,
        history,
        authorName: msg.member?.displayName || msg.author.username,
        message: msg.cleanContent.replace(`@${client.user.username}`, '').trim().slice(0, 1500),
      });
      if (text) await msg.reply({ content: text, allowedMentions: { repliedUser: false, parse: [] } });
    } catch (e) { console.error('reply failed:', e.message); }
  });

  // 3) Daily question in #general, and a Sunday leaderboard shout-out (checked every 10 minutes)
  async function scheduler() {
    try {
      const now = new Date();
      if (now.getUTCHours() !== TOPIC_HOUR_UTC) return;
      const day = now.toISOString().slice(0, 10);
      for (const guild of client.guilds.cache.values()) {
        const general = channelByName(guild, GENERAL);
        if (!general) continue;

        if (db.getKv(`topic:${guild.id}`) !== day && underDailyLimit()) {
          db.setKv(`topic:${guild.id}`, day);
          const text = await ai.dailyTopic({ dateLabel: day, launched: now.getTime() >= LAUNCH });
          if (text) await general.send({ content: text, allowedMentions: { parse: [] } });
        }

        if (now.getUTCDay() === 0 && db.getKv(`weekly:${guild.id}`) !== day) {
          db.setKv(`weekly:${guild.id}`, day);
          const top = db.leaderboard(3);
          if (top.length) {
            const medals = ['🥇', '🥈', '🥉'];
            const lines = top.map((r, i) => `${medals[i]} <@${r.user_id}> · ${r.total} pts`).join('\n');
            await general.send({
              content: `🏆 **Top Scouts this week**\n${lines}\n\nWant your name here next Sunday? Send your finds with \`/submit\` in #submit-here.`,
              allowedMentions: { users: top.map((r) => r.user_id) },
            });
          }
        }
      }
    } catch (e) { console.error('scheduler failed:', e.message); }
  }
  client.once(Events.ClientReady, () => { scheduler(); setInterval(scheduler, 10 * 60 * 1000); });
}

module.exports = { setupCommunity };
