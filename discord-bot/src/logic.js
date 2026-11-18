// Pure helpers (no Discord calls), so they can be unit-tested.
const { RANKS, ALLOWED_TYPES, MAX_FILE_MB, MAX_SUBMISSIONS_PER_DAY } = require('./config');

function rankFor(points) {
  let current = RANKS[0];
  for (const r of RANKS) if (points >= r.points) current = r;
  const next = RANKS.find((r) => r.points > points) ?? null;
  return { current, next };
}

// Returns an error message string, or null if the submission is acceptable.
function validateSubmission({ consent, contentType, sizeBytes, submittedToday }) {
  if (consent !== true) return 'You need to confirm the clip is your own recording and agree to the licence (set `consent` to True).';
  if (!contentType || !ALLOWED_TYPES.some((t) => contentType.startsWith(t)))
    return 'Only video (mp4, mov, webm) or screenshots (png, jpg, webp) are accepted.';
  if (sizeBytes > MAX_FILE_MB * 1024 * 1024) return `File is too big (max ${MAX_FILE_MB} MB).`;
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

module.exports = { rankFor, validateSubmission, safeFileName, toCsv };
