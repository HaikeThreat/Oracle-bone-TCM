# 甲骨文 · 中医密码

以手势引气，让三千年前的甲骨文在三维粒子星云中聚形 —— 每个字，都藏着一段中医密码。

![捏合聚形：粒子聚成甲骨文「心」，左侧为字形库面板](docs/screenshot.png)

**完全离线可运行 · 无任何 CDN 依赖 · 无摄像头也能玩**

## 这是什么

《智解甲骨·中医密码》—— Three.js 7000 粒子点云 + MediaPipe 手势追踪的单文件网页交互作品。摄像头手势：

| 手势 | 效果 |
| --- | --- |
| 拇指食指捏合 | **聚形**：散落的星云气聚成甲骨文 |
| 张开手掌 | **气散**：字化气回归星云 |
| 捏着左右/上下移动 | **转动视图**：位置跟随（像方向盘），手到哪转到哪；满角左右 ±66°、上下 ±60° |
| 半握移动 | 牵引星云 |
| 双手 | 各带一枚气引点 |

无摄像头时自动回退鼠标模式：按住 = 捏合聚形，松开 = 气散；鼠标是相对设备，仍为「拖动＝旋转」。

聚形收敛期间视图锁定为正视（成字那一瞬一定是正的），成字后才交还转动控制权。左下角为实时手部骨架（不显示相机画面）。

## 快速开始

摄像头手势必须在 `http://` 或 `https://` 下运行（`file://` 会被浏览器拦截：Safari 在 `file://` 下允许摄像头，却禁止 `fetch` 本地 wasm，报错只有一句 "Load failed"）：

```bash
python3 serve.py 8138
# 浏览器打开 http://localhost:8138/gesture3d.html
```

`serve.py` 是无缓存、多线程的静态服务器（只依赖标准库）。页面对此有前置拦截：在 `file://` 下点击「手势控制」会直接提示改用 HTTP，而不是抛出一句看不懂的报错。

用 `python3 -m http.server 8138` 也能跑，但浏览器容易吃缓存，且它是单线程、一个挂起连接就会让整站停止响应，不推荐。

## 字形库（面板 1066 个单字，可选 1063 个；全部经合并字表查证）

- **脏腑五行**：心（脏腑唯一见甲骨文）、木、水、火、土
- **四窍**：目（肝）、舌（心）、鼻（肺）、耳（肾）
- **身体与疾病**：疾（人卧床中矢）、龋（最早疾病记载）、齒、孕、腹、乳、母、女、首、面、囟（近"脑"）、息、见（人目正视·望诊之根）
- **医之源**：酉（医酒同源）、鬯、石（砭石刺病）、壶（悬壶济世）、虫（虫类药）、桑（桑叶入药）、麥（浮小麦养心敛汗）
- **天人自然**：风（百病之长）、雨、云、泉、兑（卦象为泽，山泽通气）、立、生（生生不息）、光（人举火照物）
- **具象物象**：马、牛、羊、虎、象、龙、鱼、燕、鳖（鳖甲入药·滋阴潜阳）、鹿（鹿茸入药）、车、舟、鼎、禾、黍、豕（六畜之一）、鼠（子时之鼠）
- **文明器物**：玉（玉石安神）、贝（贝币药市）、矢（疾之所由）、冊（典册医籍）、朋（两串贝玉相系）、卜（灼龟问吉凶）、岁（年谷之成）、狩（冬猎为狩）、用、兄（长兄如父）

> 肝、脾、肺、肾、医等字殷墟甲骨文未收录（后世字），字库中不以拟古字冒充。

> **关于「1066 / 可选 1063」**：`子`、`田`、`一` 三个字已取好码位并内嵌在子集字体中，但在页面里标了 `hidden`，不显示为面板按钮（保留备用）。想放出来就把对应条目的 `hidden: true` 删掉，面板与计数会自动更新。
>
> 数据表另有 155 条**多字条目**（`又/右/有/侑/佑/祐`、`月/夕` 这类同码位异体，以及 `祖乙`、`妣庚` 这类合文），**不进面板列表**：一个码位只对应一个字形，整条列出会显示成一长串、渲染时还会在同一画布上画多处文字互相遮挡。这些条目里每个字都收进了别名表，因此**输入单字照常能查到甲骨文**（如输入「右」→ U60491、「月」→ U605E0）。
>
> 面板按「人工编排的 67 字优先、其余按字表顺序」排列 —— 因为待机会自动巡下一字（每字约 18.4 秒），若让 1100 多个通用字混在前面，开场先看到的会是「一」「丁」「乙」这类与中医无关的字，精心挑的那批反被淹没。

## 操作速查

- 字库：控制条「字形 ▾」→ **左侧列表栏**（每行 = 字形 + 标题 + 简介，像阅读列表；可滚动，临近底部自动续载）+ 搜索（字 / 拼音 / 释义）
- 点列表条目 → 显示该字形；**再点同一条 → 隐藏**（标题与释义一并清空）。面板不自动收起，便于连续切换
- 底部「任意字·楷体」输入：**先查字库** —— 若该字有甲骨文字形，就用甲骨文渲染；库里没有才退回系统楷体（是楷体粒子字，不是甲骨文）。简繁都能查到（输入简体 `册`/`麦` 也会命中 `冊`/`麥` 的甲骨文字形），多字合并条目里的字（如 `月/夕` 的「月」）同样可查
- 颜色：五色预设（金青朱玉紫）+ 吸管自定义；实时写入顶点色
- 全屏：控制条「⛶ 全屏」
- 待机巡字：进页面后连续 45 秒无输入才启动，此后每字约 18.4 秒（聚形 1.6s → 保持 12s → 散开 1.8s → 空歇 3s），一轮 67 字约 20.5 分钟；**只在精选的 67 字里轮播**（数据里标了 `curated: true` 的字），不会轮到全库中与中医无关的字；手动选字后计时重置，若所选字不在精选池里，巡字会安全接回池首（「心」）

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `index.html` | 站点入口，跳转到 `gesture3d.html`（静态托管的目录入口必须是 index.html，否则根地址 404） |
| `gesture3d.html` | 作品主页面。字体子集与字库全部内嵌，自包含 |
| `libs/` | Three.js r152 与 MediaPipe Hands 本地运行时（约 28MB，首次访问付一次，之后走长缓存） |
| `data/` | 字表数据库（1530 行已释甲骨文）与人工编排条目 |
| `add_glyphs.py` | 往精选字库加字：并入 `data/curated_glyphs.json` 后自动调用 `build_glyphs.py` |
| `build_glyphs.py` | 唯一的构建实现：重子集化字体 + 注入页面 + 刷新别名表与计数 |
| `data/curated_glyphs.json` | **人工编排层的唯一数据源**（字头、码位、精选标记、文案） |
| `serve.py` | 无缓存本地服务器（可选）：`python3 serve.py [端口]`，默认 8138，仅本机用 `--host 127.0.0.1` |
| `deploy.py` | 生成上传就绪的站点目录 `dist/`（只挑运行时必需文件，见「部署」） |
| `deploy/` | 自建服务器辅助：`setup-server.sh` 一键配 nginx，`README.md` 说明顺序与易错点 |

## 扩充字库

```bash
python3 add_glyphs.py 牛 虎 鹿
```

新字会被并入 `data/curated_glyphs.json`（带上 `curated` 标记，因而进入待机巡字池），随后自动调用 `build_glyphs.py` 完成字体子集化与页面注入。需要 `pip install fonttools`，字必须在数据表中。刷新页面即可生效。

数据分两层，职责不重叠：

| 层 | 文件 | 作用 |
| --- | --- | --- |
| 权威字表 | `data/oracle_glyphs_full.json` | 全部已释甲骨文（字头 ↔ 码位 ↔ 拼音 ↔ 释义） |
| 人工编排 | `data/curated_glyphs.json` | 人工润色过的条目 + 精选标记，**加字只改这里** |

`build_glyphs.py` 是唯一的构建实现（`add_glyphs.py` 也复用它）：

```bash
python3 build_glyphs.py              # 全量重建（读上表两个数据文件）
python3 build_glyphs.py --limit 200  # 只取前 200 个，试体积用
python3 build_glyphs.py --db 其它.json --curated 其它.json   # 换数据源
```

实测体积：面板约 1066 个单字，字体子集（二进制）约 **962KB**、页面内嵌 base64 约 **1.25MB**、整个 HTML 约 **1.5MB**（相比手势模型的 16MB 仍属小头）。字库数据已与主脚本分离：条目与别名表写在页面头部，重建只改动那两块。

## 部署

**硬性前提：必须 HTTPS。** 非 `localhost` 的 HTTP 页面不是「安全上下文」，浏览器**不提供摄像头**，手势功能直接不可用。GitHub Pages 自带 HTTPS；自建服务器需自行配证书。

### 方式一：GitHub Pages

仓库 **Settings → Pages → Deploy from a branch** 选 `main` / `(root)`。
资源全部使用相对路径，已实测子路径（`用户名.github.io/仓库名/`）下可正常运行。

### 方式二：自建服务器（阿里云等）

先生成上传就绪的目录，再上传并配置服务器：

```bash
python3 deploy.py                                  # ① 本地：输出 dist/，16 个文件约 25MB
rsync -avz --delete dist/ root@<ECS公网IP>:/var/www/oracletcm/   # ② 上传
sudo bash deploy/setup-server.sh oracletcm.com /var/www/oracletcm  # ③ 服务器：配 nginx
```

`deploy/setup-server.sh` 会装 nginx、写入下文那份配置、放行防火墙；它是幂等的，
且**先探测证书** —— 没有证书时先写「仅 HTTP」配置让站点能开（否则 nginx 因引用不存在的
证书而起不来），证书就绪后重跑即自动切换为 HTTPS。详见 [`deploy/README.md`](deploy/README.md)。

脚本只挑**运行时真正需要**的文件，并显式保留两类「没被请求但删不得」的 fallback：
`hands_solution_wasm_bin.{js,wasm}`（旧浏览器无 SIMD 时用）与 `hand_landmark_lite.tflite`（`modelComplexity:0` 时用）。
不纳入 `libs/AYJGW.ttf`（4.2MB）—— 那是构建时子集化用的完整字体，页面内嵌的是 base64 子集。

把 `dist/` 内容上传到站点根后，nginx 关键配置：

```nginx
server {
    listen 443 ssl http2;
    server_name 你的域名;
    ssl_certificate     /etc/nginx/ssl/你的域名.pem;
    ssl_certificate_key /etc/nginx/ssl/你的域名.key;

    root /var/www/oracle;
    index index.html;

    # 必须：.wasm 的 MIME（默认 octet-stream 会让 MediaPipe 走慢速回退）
    types { application/wasm wasm; }
    include /etc/nginx/mime.types;

    gzip on;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_types text/html text/css application/javascript text/javascript application/json;

    # libs/ 长缓存（首屏约 16MB，只在首次付）；页面用顶部 ASSET_V 破缓存
    location /libs/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
        gzip off;              # wasm/tflite 已是压缩格式，再压无益
        try_files $uri =404;
    }
    location ~ \.html$ { add_header Cache-Control "no-cache"; }

    client_max_body_size 32m;
}
server { listen 80; server_name 你的域名; return 301 https://$host$request_uri; }
```

压缩收益（实测）：`gesture3d.html` 1550→**831KB**、
`hands_solution_simd_wasm_bin.wasm` 5885→**1773KB**、`three.min.js` 618→**154KB**。

安全组只放行 **443**（与 80 用于跳转）。**不要把 `serve.py` 的 8138 端口暴露到公网** —— 它面向本地开发，没有访问控制。

## License 与致谢

- 本项目代码以 [MIT](LICENSE) 许可发布；第三方字体与数据各自按其许可发布，状态见 [THIRD-PARTY-NOTICE.md](THIRD-PARTY-NOTICE.md)
- 甲骨文字形数据：[甲骨文AI协同平台](https://jgwlbq.org.cn)（甲骨文合并字表）
- 甲骨文字体：AYJGW
- 渲染与手势：[Three.js](https://threejs.org)（MIT）、[MediaPipe Hands](https://developers.google.com/mediapipe)（Apache 2.0）
