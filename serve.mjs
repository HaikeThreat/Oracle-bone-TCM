// 跨平台静态服务器（Node.js，无第三方依赖）——保证 Windows / macOS / Linux 都能跑。
// 用法：node serve.mjs [端口] [--host 地址]      默认 127.0.0.1:8138
// 需要其它设备访问时：node serve.mjs 8138 --host 0.0.0.0
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, join, normalize, sep, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

// 兼容取脚本目录（Node / Bun 通用）
const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = __dirname;   // 以脚本所在目录为站点根，避免依赖启动时的工作目录
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.wasm': 'application/wasm',
  '.tflite': 'application/octet-stream',
  '.data': 'application/octet-stream',
  '.map': 'application/json; charset=utf-8',
  '.pdf': 'application/pdf',
};

const args = process.argv.slice(2);
const port = parseInt(args.find(a => /^\d+$/.test(a)) || '8138', 10);
const hostIdx = args.indexOf('--host');
const host = hostIdx >= 0 ? args[hostIdx + 1] : '127.0.0.1';

const server = createServer(async (req, res) => {
  try {
    let urlPath = decodeURIComponent(new URL(req.url, 'http://x').pathname);
    if (urlPath === '/' || urlPath === '') urlPath = '/index.html';
    // 防目录穿越：规范化后必须仍在 ROOT 之内
    const safeRel = normalize(urlPath).replace(/^([/\\])+/, '');
    const filePath = join(ROOT, safeRel);
    if (!filePath.startsWith(ROOT + sep) && filePath !== ROOT) {
      res.writeHead(403); res.end('Forbidden'); return;
    }
    const st = await stat(filePath).catch(() => null);
    if (!st || !st.isFile()) { res.writeHead(404); res.end('Not Found'); return; }
    const ext = extname(filePath).toLowerCase();
    const isImmutable = urlPath.startsWith('/libs/');
    const data = await readFile(filePath);
    res.writeHead(200, {
      'Content-Type': MIME[ext] || 'application/octet-stream',
      'Content-Length': data.length,
      'Cache-Control': isImmutable ? 'public, max-age=31536000, immutable' : 'no-cache',
    });
    res.end(data);
  } catch (e) {
    res.writeHead(500); res.end('Internal Error: ' + e.message);
  }
});

server.listen(port, host, () => {
  console.log(`Serving ${ROOT} at http://${host}:${port}/  (入口 index.html)`);
});
