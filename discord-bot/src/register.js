// Registers slash commands on your server (instant) — run once, and again after changing commands.js.
const { REST, Routes } = require('discord.js');
const { env } = require('./config');
const { commands } = require('./commands');

(async () => {
  const rest = new REST().setToken(env('DISCORD_TOKEN'));
  await rest.put(Routes.applicationGuildCommands(env('CLIENT_ID'), env('GUILD_ID')), { body: commands });
  console.log(`Registered ${commands.length} commands.`);
})().catch((e) => { console.error(e); process.exit(1); });
