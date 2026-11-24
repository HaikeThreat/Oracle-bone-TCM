// Bun 版静态服务器（若有 Bun，速度更快）；无 Bun 请用 node serve.mjs。
// 以脚本所在目录为站点根，避免依赖启动时的工作目录（换系统更稳）。
import { fileURLToPath } from 'node:url';
import { dirname, join as pathJoin } from 'node:path';

const ROOT = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.argv[2] || '8138', 10);
const HOST = process.argv.includes('--host')
  ? process.argv[process.argv.indexOf('--host') + 1] : '127.0.0.1';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp',
  '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf',
  '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json',
  '.wasm': 'application/wasm', '.tflite': 'application/octet-stream',
  '.data': 'application/octet-stream', '.map': 'application/json; charset=utf-8',
  '.pdf': 'application/pdf',
};

Bun.serve({
  port: PORT,
  hostname: HOST,
  fetch(req) {
    const url = new URL(req.url);
    let p = decodeURIComponent(url.pathname);
    if (p === '/') p = '/index.html';
    const rel = p.replace(/^\/+/, '');
    const filePath = pathJoin(ROOT, rel);
    if (!filePath.startsWith(ROOT)) return new Response('Forbidden', { status: 403 });
    const ext = p.slice(p.lastIndexOf('.')).toLowerCase();
    const file = Bun.file(filePath);
    return new Response(file, {
      headers: {
        'Content-Type': MIME[ext] || 'application/octet-stream',
        'Cache-Control': p.startsWith('/libs/')
          ? 'public, max-age=31536000, immutable' : 'no-cache',
      },
    });
  },
});
console.log(`Serving ${ROOT} at http://${HOST}:${PORT}/`);
