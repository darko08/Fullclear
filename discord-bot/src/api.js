// Small public read-only API for the website map: approved finds + their media.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const ALLOWED_ORIGINS = ['https://fullclearmap.com', 'https://www.fullclearmap.com', 'https://fullclearmap.netlify.app'];
const TYPES = { '.mp4': 'video/mp4', '.mov': 'video/quicktime', '.webm': 'video/webm', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' };

function startApi(db) {
  const port = Number(process.env.PORT || 0);
  if (!port) { console.log('Map API off (no PORT set)'); return; }

  http.createServer((req, res) => {
    const origin = req.headers.origin;
    if (ALLOWED_ORIGINS.includes(origin)) res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin');
    if (req.method !== 'GET' && req.method !== 'HEAD') { res.writeHead(405); return res.end(); }
    const url = new URL(req.url, 'http://x');

    if (url.pathname === '/api/finds') {
      const finds = db.publicFinds().map((f) => ({
        id: f.id, category: f.category, location: f.location, description: f.description,
        credit: f.credit_name, x: f.map_x, y: f.map_y, approvedAt: f.reviewed_at,
        media: f.file_path ? `/media/${f.id}${path.extname(f.file_path).toLowerCase()}` : null,
      }));
      res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=60' });
      return res.end(JSON.stringify({ finds }));
    }

    const m = url.pathname.match(/^\/media\/(\d+)\.[a-z0-9]+$/);
    if (m) {
      const f = db.publicFinds().find((x) => x.id === Number(m[1]));
      if (!f?.file_path || !fs.existsSync(f.file_path)) { res.writeHead(404); return res.end(); }
      const size = fs.statSync(f.file_path).size;
      const type = TYPES[path.extname(f.file_path).toLowerCase()] || 'application/octet-stream';
      const range = req.headers.range?.match(/bytes=(\d*)-(\d*)/);
      if (range) { // video seeking
        const start = range[1] ? Number(range[1]) : 0;
        const end = range[2] ? Math.min(Number(range[2]), size - 1) : size - 1;
        res.writeHead(206, { 'Content-Type': type, 'Content-Range': `bytes ${start}-${end}/${size}`, 'Accept-Ranges': 'bytes', 'Content-Length': end - start + 1, 'Cache-Control': 'public, max-age=86400' });
        return fs.createReadStream(f.file_path, { start, end }).pipe(res);
      }
      res.writeHead(200, { 'Content-Type': type, 'Content-Length': size, 'Accept-Ranges': 'bytes', 'Cache-Control': 'public, max-age=86400' });
      return fs.createReadStream(f.file_path).pipe(res);
    }

    if (url.pathname === '/health') { res.writeHead(200); return res.end('ok'); }
    res.writeHead(404); res.end();
  }).listen(port, () => console.log(`Map API on :${port}`));
}

module.exports = { startApi };
