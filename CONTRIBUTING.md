# 协作与提交说明

本仓库的 `main` 是**发布分支**，已开启分支保护：不允许直接推送，所有改动必须通过 Pull Request（PR），并由仓库所有者批准后合并。

## 一、合作者：改代码的流程

### 1. 每次先同步最新 main

```bash
git fetch origin
git checkout main
git reset --hard origin/main
```

> ⚠️ 不要拿本地旧副本直接覆盖仓库文件。如果本地版本落后，先执行上面的同步；基于旧版提交会把已合并的新功能「回退」掉。

### 2. 开一个自己的分支

```bash
git checkout -b feature/简短说明
```

### 3. 修改并本地预览

```bash
python3 serve.py 8138
# 浏览器打开 http://localhost:8138
```

macOS 也可以直接双击根目录的 `启动本地服务.command`。手势功能必须通过 `http://` 访问，直接双击 `index.html`（`file://`）只能看展厅，手势会被浏览器拦截。

提交前建议自查：

- 扉页能正常进入，两个展厅都能打开
- 中药展厅的三七模型正常显示
- 手势控制可用；不可用时鼠标模式仍能操作
- 手机竖屏下布局正常

### 4. 提交并推送分支

```bash
git add -A
git commit -m "简短说明这次改了什么"
git push -u origin feature/简短说明
```

推送分支是允许的；**直接 `git push origin main` 会被拒绝**（提示 `protected branch`），这是正常现象。

### 5. 开 Pull Request

在 GitHub 上进入本仓库，点击 **Compare & pull request**：

- base 选 `main`，compare 选你的分支
- 写清楚：改了什么、为什么改、怎么验证的（有截图更好）
- 点击 **Create pull request**

### 6. 等待审核

- 审核通过（Approve）后，PR 才允许合并
- 如果需要修改（Request changes），改完再次推送即可；**新推送会让之前的批准失效**，需要重新审核
- 不要在审核期间直接改动 `main`

## 二、仓库所有者：审核流程

在 PR 页面：

1. **Files changed** → 逐行检查改动
2. **Review changes** → **Approve**（或 **Request changes** 并写明原因）
3. 回到 Conversation 页 → **Merge pull request**

命令行方式：

```bash
gh pr list                    # 列出待审 PR
gh pr diff <编号>             # 查看改动
gh pr review <编号> --approve # 批准
gh pr review <编号> --request-changes --body "需要修改的地方"
gh pr merge <编号> --merge    # 合并
```

## 三、合并之后

- **GitHub Pages（备用入口）** 会从 `main` 自动构建并部署：
  <https://haikethreat.github.io/Oracle-bone-TCM/>
- **主站 `oracletcm.com` 不会自动更新**，需要仓库所有者按 `deploy/README.md` 执行：
  ```bash
  python3 deploy.py
  rsync -avz --delete dist/ root@<SWAS公网IP>:/var/www/oracletcm/
  ```

## 四、提交约定

- 提交信息用中文，写清「改了什么」，例如：`扉页：修复打光层色阶`、`展厅：调整三七模型缩放`
- 一个 PR 尽量只做一件事，便于审核和回退
- 本仓库是**公开仓库**：不要提交密钥、账号密码、`.env`、个人隐私材料
- 新增较大的二进制资源（模型、字体等）前先与仓库所有者沟通，避免仓库体积失控
- 改动涉及第三方素材时，同步更新 `THIRD-PARTY-NOTICE.md`

## 五、出问题怎么办

- 分支落后导致冲突：先 `git fetch origin && git rebase origin/main`，解决冲突后再推送
- 不小心把旧版文件提交进 PR：不要强推 `main`，关闭 PR、重新从最新 `main` 开分支整理即可
- 不确定怎么操作：先在 PR 里说明情况，不要直接改 `main`
