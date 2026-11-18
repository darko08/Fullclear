// Slash command definitions. Registered with `npm run register`.
const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { CATEGORIES } = require('./config');

const commands = [
  new SlashCommandBuilder()
    .setName('submit')
    .setDescription('Submit your own clip or screenshot of a find')
    .addAttachmentOption((o) => o.setName('clip').setDescription('Your video or screenshot').setRequired(true))
    .addStringOption((o) => o.setName('category').setDescription('What is it?').setRequired(true)
      .addChoices(...CATEGORIES.map((c) => ({ name: c, value: c }))))
    .addStringOption((o) => o.setName('location').setDescription('Where is it? (area, landmark, nearest road)')
      .setRequired(true).setMaxLength(200))
    .addStringOption((o) => o.setName('description').setDescription('What did you find / how do you get it?')
      .setRequired(true).setMaxLength(500))
    .addBooleanOption((o) => o.setName('consent')
      .setDescription('True = I recorded this myself and agree to the Full Clear clip licence (see #rules)')
      .setRequired(true))
    .addStringOption((o) => o.setName('credit').setDescription('Name to credit in videos (default: your username)')
      .setMaxLength(40)),

  new SlashCommandBuilder().setName('profile').setDescription('Your points, rank and approved clips'),

  new SlashCommandBuilder().setName('leaderboard').setDescription('Top contributors'),

  new SlashCommandBuilder()
    .setName('setpin')
    .setDescription('Moderators: place an approved find on the website map')
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages)
    .addIntegerOption((o) => o.setName('id').setDescription('Submission number, e.g. 12').setRequired(true).setMinValue(1))
    .addNumberOption((o) => o.setName('x').setDescription('Map X, 0 (left) to 1000 (right)').setRequired(true).setMinValue(0).setMaxValue(1000))
    .addNumberOption((o) => o.setName('y').setDescription('Map Y, 0 (bottom) to 1000 (top)').setRequired(true).setMinValue(0).setMaxValue(1000)),

  new SlashCommandBuilder()
    .setName('export')
    .setDescription('Moderators: download approved clips list (CSV) for the editor')
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages)
    .addIntegerOption((o) => o.setName('days').setDescription('How many days back (default 7)')
      .setMinValue(1).setMaxValue(90)),
];

module.exports = { commands: commands.map((c) => c.toJSON()) };
