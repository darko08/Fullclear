const test = require('node:test');
const assert = require('node:assert');
const { rankFor, validateSubmission, safeFileName, toCsv } = require('../src/logic');
const { openDb } = require('../src/db');

const ok = { consent: true, contentType: 'video/mp4', sizeBytes: 5e6, submittedToday: 0 };

test('ranks', () => {
  assert.equal(rankFor(0).current.role, 'Rookie');
  assert.equal(rankFor(29).next.role, 'Pathfinder');
  assert.equal(rankFor(100).current.role, 'Cartographer');
  assert.equal(rankFor(999).next, null);
});

test('validation', () => {
  assert.equal(validateSubmission(ok), null);
  assert.match(validateSubmission({ ...ok, consent: false }), /licence/);
  assert.match(validateSubmission({ ...ok, contentType: 'application/zip' }), /Only video/);
  assert.match(validateSubmission({ ...ok, sizeBytes: 500e6 }), /too big/);
  assert.match(validateSubmission({ ...ok, submittedToday: 10 }), /limit/);
});

test('file names and csv', () => {
  assert.equal(safeFileName(7, '../../evil clip.MP4'), '000007.mp4');
  assert.equal(safeFileName(7, 'noext'), '000007');
  assert.equal(toCsv([{ id: 1, description: 'a, "b"' }]).split('\n')[1].split(',')[0], '1');
  assert.match(toCsv([{ id: 1, description: 'a, "b"' }]), /"a, ""b"""/);
});

test('db review flow and points', () => {
  const db = openDb(':memory:');
  const id = db.addSubmission({ userId: 'u1', userTag: 'ana', category: 'Easter egg', location: 'Beach', description: 'x', creditName: 'ana' });
  assert.equal(db.pendingToday('u1'), 1);
  assert.equal(db.review(id, 'approved', 'mod'), true);
  assert.equal(db.review(id, 'rejected', 'mod'), false, 'cannot review twice');
  assert.equal(db.addPoints('u1', 'ana', 10), 10);
  assert.equal(db.addPoints('u1', 'ana', 25), 35);
  assert.equal(db.leaderboard()[0].total, 35);
  assert.equal(db.countByUser('u1', 'approved'), 1);
  assert.equal(db.approvedSince('2000-01-01').length, 1);
});
