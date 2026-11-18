// Pure helpers (no Discord calls), so they can be unit-tested.
const { RANKS, ALLOWED_TYPES, MAX_FILE_MB, MAX_SUBMISSIONS_PER_DAY } = require('./config');

function rankFor(points) {
  let current = RANKS[0];
  for (const r of RANKS) if (points >= r.points) current = r;
  const next = RANKS.find((r) => r.points > points) ?? null;
  return { current, next };
}

// Returns an error message string, or null if the submission is acceptable.
// Video links we accept when the file is too big for Discord (own uploads only; consent still required).
const LINK_HOSTS = ['youtube.com', 'youtu.be', 'tiktok.com', 'drive.google.com', 'streamable.com', 'medal.tv',
  'x.com', 'twitter.com', 'instagram.com', 'dropbox.com', 'twitch.tv', 'outplayed.tv'];

// Returns the normalised https URL if it is an accepted video link, else null.
function parseClipLink(link) {
  if (!link) return null;
  let u;
  try { u = new URL(link.trim()); } catch { return null; }
  if (u.protocol !== 'https:' || u.username || u.password) return null;
  const host = u.hostname.toLowerCase().replace(/^(www|m|vm|clips)\./, '');
  return LINK_HOSTS.some((h) => host === h || host.endsWith(`.${h}`)) ? u.toString() : null;
}

function validateSubmission({ consent, contentType, sizeBytes, link, submittedToday }) {
  if (consent !== true) return 'You need to confirm the clip is your own recording and agree to the licence (set `consent` to True).';
  const hasFile = contentType != null || sizeBytes != null;
  if (!hasFile && !link) return 'Attach your clip (`clip`) or paste a link to it (`link`), e.g. YouTube, TikTok or Google Drive.';
  if (hasFile && link) return 'Use either `clip` (file) or `link`, not both.';
  if (link) {
    if (!parseClipLink(link)) return `That link isn't accepted. Use an https link from: ${LINK_HOSTS.join(', ')}.`;
  } else {
    if (!contentType || !ALLOWED_TYPES.some((t) => contentType.startsWith(t)))
      return 'Only video (mp4, mov, webm) or screenshots (png, jpg, webp) are accepted.';
    if (sizeBytes > MAX_FILE_MB * 1024 * 1024)
      return `File is too big (max ${MAX_FILE_MB} MB). Upload it to YouTube, TikTok or Google Drive and use \`link\` instead.`;
  }
  if (submittedToday >= MAX_SUBMISSIONS_PER_DAY)
    return `You've hit today's limit of ${MAX_SUBMISSIONS_PER_DAY} submissions. Thanks for the hustle, try again tomorrow.`;
  return null;
}

function safeFileName(id, original) {
  const ext = (original.match(/\.[a-z0-9]{2,5}$/i)?.[0] ?? '').toLowerCase();
  return `${String(id).padStart(6, '0')}${ext}`;
}

function csvEscape(v) {
  const s = v == null ? '' : String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function toCsv(rows) {
  const cols = ['id', 'category', 'location', 'description', 'credit_name', 'user_tag', 'file_path', 'reviewed_at'];
  return [cols.join(','), ...rows.map((r) => cols.map((c) => csvEscape(r[c])).join(','))].join('\n');
}

module.exports = { rankFor, validateSubmission, parseClipLink, LINK_HOSTS, safeFileName, toCsv };
