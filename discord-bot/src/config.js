// All tunables in one place. Secrets and IDs come from environment variables (see .env.example).
const CATEGORIES = [
  'Collectible', 'Hidden location', 'Easter egg', 'Money method', 'Vehicle',
  'Weapon', 'Side activity', 'Glitch / funny moment', 'Tip / mechanic',
];

// Contributor ranks: role names must exist on the server (see SERVER-BLUEPRINT.md).
const RANKS = [
  { points: 0,   role: 'Rookie' },
  { points: 30,  role: 'Pathfinder' },
  { points: 100, role: 'Cartographer' },
  { points: 300, role: 'Legend' },
];

const POINTS = { approved: 10, featured: 25 };

// Text shown and agreed to on every submission. Keep in sync with #rules.
const LICENSE_TEXT =
  'I recorded this clip myself (it is my own gameplay). I give Full Clear a non-exclusive, ' +
  'worldwide, royalty-free licence to edit and publish it on its website and social channels, ' +
  'with credit to the name I provide. I can ask for removal at any time.';

function env(name, fallback) {
  const v = process.env[name];
  if (v === undefined || v === '') {
    if (fallback !== undefined) return fallback;
    throw new Error(`Missing environment variable ${name} (see .env.example)`);
  }
  return v;
}

module.exports = {
  CATEGORIES, RANKS, POINTS, LICENSE_TEXT,
  MAX_FILE_MB: 100,
  MAX_SUBMISSIONS_PER_DAY: 10,
  ALLOWED_TYPES: ['video/mp4', 'video/quicktime', 'video/webm', 'image/png', 'image/jpeg', 'image/webp'],
  env,
};
