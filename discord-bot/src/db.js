// Storage for clip submissions and contributor points (built-in node:sqlite, no native deps).
const { DatabaseSync } = require('node:sqlite');
const path = require('node:path');
const fs = require('node:fs');

function openDb(file) {
  if (file !== ':memory:') fs.mkdirSync(path.dirname(file), { recursive: true });
  const db = new DatabaseSync(file);
  db.exec(`
    CREATE TABLE IF NOT EXISTS submissions (
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id       TEXT NOT NULL,
      user_tag      TEXT NOT NULL,
      category      TEXT NOT NULL,
      location      TEXT NOT NULL,
      description   TEXT NOT NULL,
      credit_name   TEXT NOT NULL,
      file_path     TEXT,
      source_url    TEXT,
      status        TEXT NOT NULL DEFAULT 'pending',   -- pending | approved | rejected
      reviewer_id   TEXT,
      reject_reason TEXT,
      created_at    TEXT NOT NULL DEFAULT (datetime('now')),
      reviewed_at   TEXT
    );
    CREATE TABLE IF NOT EXISTS kv (
      key   TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS points (
      user_id  TEXT PRIMARY KEY,
      user_tag TEXT NOT NULL,
      total    INTEGER NOT NULL DEFAULT 0
    );
  `);

  // Map coordinates (0–1000 on both axes), set by moderators with /setpin.
  const cols = db.prepare('PRAGMA table_info(submissions)').all().map((c) => c.name);
  if (!cols.includes('map_x')) db.exec('ALTER TABLE submissions ADD COLUMN map_x REAL');
  if (!cols.includes('map_y')) db.exec('ALTER TABLE submissions ADD COLUMN map_y REAL');

  return {
    raw: db,
    setPin(id, x, y) {
      return db.prepare("UPDATE submissions SET map_x = ?, map_y = ? WHERE id = ? AND status = 'approved'").run(x, y, id).changes === 1;
    },
    publicFinds() {
      return db.prepare(`SELECT id, category, location, description, credit_name, file_path, map_x, map_y, reviewed_at
        FROM submissions WHERE status = 'approved' ORDER BY reviewed_at DESC LIMIT 2000`).all();
    },
    addSubmission(s) {
      const r = db.prepare(`INSERT INTO submissions
        (user_id, user_tag, category, location, description, credit_name, file_path, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)`).run(
        s.userId, s.userTag, s.category, s.location, s.description, s.creditName,
        s.filePath ?? null, s.sourceUrl ?? null);
      return Number(r.lastInsertRowid);
    },
    getSubmission(id) {
      return db.prepare('SELECT * FROM submissions WHERE id = ?').get(id);
    },
    // Returns true only if the submission was still pending (prevents double-review).
    review(id, status, reviewerId, reason = null) {
      const r = db.prepare(`UPDATE submissions SET status = ?, reviewer_id = ?, reject_reason = ?,
        reviewed_at = datetime('now') WHERE id = ? AND status = 'pending'`).run(status, reviewerId, reason, id);
      return r.changes === 1;
    },
    addPoints(userId, userTag, amount) {
      db.prepare(`INSERT INTO points (user_id, user_tag, total) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET total = total + excluded.total, user_tag = excluded.user_tag`)
        .run(userId, userTag, amount);
      return db.prepare('SELECT total FROM points WHERE user_id = ?').get(userId).total;
    },
    getPoints(userId) {
      return db.prepare('SELECT total FROM points WHERE user_id = ?').get(userId)?.total ?? 0;
    },
    leaderboard(limit = 10) {
      return db.prepare('SELECT user_id, user_tag, total FROM points ORDER BY total DESC LIMIT ?').all(limit);
    },
    countByUser(userId, status) {
      return db.prepare('SELECT COUNT(*) AS n FROM submissions WHERE user_id = ? AND status = ?').get(userId, status).n;
    },
    pendingToday(userId) {
      return db.prepare(`SELECT COUNT(*) AS n FROM submissions
        WHERE user_id = ? AND created_at >= datetime('now', '-1 day')`).get(userId).n;
    },
    getKv(key) {
      return db.prepare('SELECT value FROM kv WHERE key = ?').get(key)?.value ?? null;
    },
    setKv(key, value) {
      db.prepare('INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value')
        .run(key, String(value));
    },
    approvedSince(sinceIso) {
      return db.prepare(`SELECT * FROM submissions WHERE status = 'approved' AND reviewed_at >= ?
        ORDER BY reviewed_at`).all(sinceIso);
    },
  };
}

module.exports = { openDb };
