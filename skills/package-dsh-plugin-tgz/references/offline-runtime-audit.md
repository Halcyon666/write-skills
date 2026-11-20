# 离线运行时自包含审计（装得上 ≠ 能用）

`pack-plugin.cmd` 只保证 tgz **离线可安装**（依赖在包里、hash 对）。它管不到插件**运行时**会不会再联网下载。`next-ai-drawio/dsh` 插件就是典型：打包成功、离线安装成功，但第一次运行卡在 `npx -y @next-ai-drawio/mcp-server@latest`——npx 要去 registry 拉包，没网就卡死。

所以交付离线包前，一定要做这层审计。核心原则：**插件从冷启动到工具可用，全程不能发起任何下载**。

## 1. 找远程下载

打开插件的 `cordis.patch.yml`、其它启动配置、以及 `package.json` 的脚本，搜这些模式：

```
npx  uvx  @latest  curl  wget  git clone  https://...registry...  pip install  npm i
```

按场景判断：

- **普通插件**（有真实 `dependencies`）：依赖已被脚本内联进 `node_modules`，只要启动时不再 `npm install`/下载，就 OK。
- **配置型 MCP bundle**（`package.json` 里 `dsh.bundle.patch` 指向 `cordis.patch.yml`，本身零依赖）：危险。它通常只是把 server 的配置交给 `@deepseek-ai/dsh-mcp-client`，而配置里如果是 `command: npx` + `args: [-y, xxx@latest]`，运行时必然下载。

## 2. 修法：把服务 vendor 进插件，改成本地启动

流程（drawio 插件实战验证过）：

### a. 找到可直接运行的 server 产物

如果是 npx 启动的，先看本机 npx 缓存里有没有下载好的完整包：

```
%LOCALAPPDATA%\npm-cache\_npx\<hash>\node_modules\
```

里面通常有 `@scope/pkg/dist`（真正代码）+ 平铺的全部依赖。确认这个包**能离线独立跑**：

- `package.json` 的 `type: module`、`bin`/`main` 指向 `dist/index.js`。
- `dist/` 里若自带静态资源（如 drawio 的 `dist/drawio/`、`dist/shell/`），确认无 CDN/https 引用——有就是运行时也会联网。
- 依赖要一起带上：server 自己一般没有 `node_modules`，依赖是平铺在缓存 `node_modules` 里的。

### b. 组织 vendor 目录

在插件源码根目录下建：

```
<plugin>/
  vendor/
    mcp-server/
      dist/            <- server 的 dist（含静态资源）
      package.json     <- server 的 package.json，必须带！
    node_modules/      <- server 的全部依赖（平铺拷贝）
```

**必须把 server 的 `package.json` 也拷进 `vendor/mcp-server/`**：实测缺了它，server 里读自身版本的逻辑（如 `dist/http-server.js`）会 `ENOENT .../vendor/mcp-server/package.json` 崩掉。

**复制目录树的 PowerShell 坑**：`Copy-Item -LiteralPath "...\dist\*"` 不会展开通配符、什么都不会复制。要复制目录就直接指目录：

```powershell
Copy-Item -Path "$cache\@scope\mcp-server\dist" -Destination "$stage\vendor\mcp-server\dist" -Recurse -Force
Copy-Item -Path "$cache\@scope\mcp-server\package.json" -Destination "$stage\vendor\mcp-server\package.json" -Force
Copy-Item -Path "$cache\node_modules" -Destination "$stage\vendor\node_modules" -Recurse -Force
```

注意：`target\vendor\node_modules` 若已存在，`Copy-Item -Recurse` 的落点可能变成 `vendor\node_modules\node_modules`——用前先确认目标不存在，或逐个顶层条目复制。

### c. 改 package.json

把 `vendor` 加进 `files`，这样 `npm pack` 才会把 vendor 打进 tgz（零依赖插件没有 `bundleDependencies` 机制，全靠 `files`）：

```json
{
  "name": "@scope/plugin",
  "version": "0.1.0",
  "files": ["cordis.patch.yml", "icon.png", "locale", "README.md", "vendor"],
  "dsh": { "bundle": { "patch": "./cordis.patch.yml" } }
}
```

实测：只要 `files` 含 `vendor`，`npm pack` 会保留 `package/vendor/node_modules/...` 的完整层级。

### d. 改 cordis.patch.yml 用本地启动

原来的远程启动：

```yaml
- insert:
    - id: mcp-drawio
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: drawio
        transport: stdio
        command: npx
        args: ['-y', '@scope/mcp-server@latest']
        env: { DRAWIO_ALLOW_EMBED: 'true', BROWSER: none }
```

改成 vendored 本地启动：

```yaml
- insert:
    - id: mcp-drawio
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: drawio
        transport: stdio
        command: !!js process.execPath
        args:
          - !!js ctx.get('profileContext').dir + '/node_modules/@scope/plugin/vendor/mcp-server/dist/index.js'
        cwd: !!js ctx.get('profileContext').dir + '/node_modules/@scope/plugin/vendor/mcp-server'
        toolCallTimeoutMs: 120000
        env:
          DRAWIO_ALLOW_EMBED: 'true'
          BROWSER: none
          ELECTRON_RUN_AS_NODE: '1'
```

要点和为什么：

- `command: !!js process.execPath` —— 在 DSH 里 `process.execPath` 是 Harness 的 Electron exe；配 `env.ELECTRON_RUN_AS_NODE: '1'` 后它 behave 成纯 Node，能直接跑 ESM server。这样不用假设 `node` 在 PATH 上，也不用写死某个 `node.exe` 的绝对路径。
- `!!js` 是 YAML 标签，值在插件 ctx 里 eval（`new Function('ctx','expr','with(ctx){return eval(expr)}')`）。`ctx.get('profileContext').dir` 是当前 profile 目录——**profile 名无关**，比 `dshHomePath('profiles','desktop',...)` 稳。
- **数组里的 `!!js` 要用块写法**（`args:\n  - !!js <expr>`）。写成 flow `args: [!!js expr]` 会 YAML 解析失败：`missed comma between flow collection entries`。
- `!!js` 在 `--dump-config` 里会原样保留（插值发生得更晚，在 fiber config 阶段），所以 dump-config 看不到展开后的路径是正常的。
- `cwd` 指到 vendored server 根，让 server 的相对资源路径能正确解析。
- `BROWSER: none` 只是让 `start_session` 不自动开浏览器、改为在结果里返回预览链接；`DRAWIO_ALLOW_EMBED: 'true'` 让 DSH 侧边栏 iframe 能嵌预览。都不影响联网。
- `toolCallTimeoutMs` 视情况调大（截图/导出慢）。

## 3. 打包 + 实测

1. 用 `pack-plugin.cmd` 打包（本技能主流程）。零依赖插件走 `no runtime deps to inline` 分支。
2. `tar -tzf <tgz>` 确认 `package/vendor/mcp-server/dist/index.js`、`package/vendor/node_modules/...` 都在，且 patch 里没有 `npx`/`@latest`。
3. **离线安装 + 真正启动**（关键，别省）：
   - 建临时 profile：package.json 里 dep 写 `file:` 指向 tgz，配 `pnpm-workspace.yaml`（`nodeLinker: hoisted`、`autoInstallPeers: false`）。
   - 用 DSH 自带 pnpm 离线装：
     ```
     node "<DSH 安装目录>\resources\runtime\primary-runtime\dependencies\pnpm\dist\pnpm.mjs" install --offline --ignore-scripts
     ```
     注意 `--no-audit`/`--no-fund` 是这个 pnpm 的**未知选项**，别加。
   - 装完写一个 stdio 探针 spawn `vendored dist/index.js`（用 harness exe + `ELECTRON_RUN_AS_NODE=1` 或普通 node 都行），发 `initialize` + `tools/list`，确认返回预期工具数、stderr 是 `... running on stdio`、无联网下载日志。
   - 顺带 eval 一遍 `!!js` 路径表达式，确认拼出来的 `index.js`/`cwd` 真实存在。
4. 若把改过的 tgz 装进桌面 profile：同步更新该 profile `pnpm-lock.yaml` 里这个 tgz 的 `integrity`（新 sha512），否则 `--frozen-lockfile` 会报 `ERR_PNPM_TARBALL_INTEGRITY` checksum 不匹配。算 hash：
   ```
   node -e "const c=require('crypto'),f=require('fs'),b=f.readFileSync(process.argv[1]);console.log('sha512-'+c.createHash('sha512').update(b).digest('base64'))" <tgz>
   ```

## 4. 其它 agent 复用这个 MCP

- **DSH 内部 agent**：bundle 装一次、重启 DSH、开**新会话**即可。mcp-client 把工具注册到共享 `ctx.tools`（`mcp__drawio__<name>`），所有 agent 共用，无需各自配置。旧会话保留的是加载时的插件版本，看不到新工具。
- **外部 agent**（Claude Code / Cursor / Codex / VS Code）：各家写标准 stdio MCP 配置，`command` 指 vendored `dist/index.js`（外部客户端没有 `process.execPath` 这套，直接用 node 可执行文件的绝对路径），`cwd` 和 `env` 同上。每个客户端各自 spawn 一个进程；若 server 用固定端口，注意多实例端口冲突；共享的数据目录（如 drawio 自动保存到 `~/.next-ai-drawio`）可用环境变量隔离。

## 5. 参考：drawio 实测数据点

- vendored server `@next-ai-drawio/mcp-server@0.4.15`，`dist` 自带 draw.io v32.0.2 静态资源，无 CDN 引用。
- npx 缓存 node_modules 约 65 MB / 7332 文件 / 121 顶层条目；全部 vendor 后 tgz 约 33.97 MB / 9771 文件。
- 本地启动 `tools/list` 返回 16 个工具（get_drawing_guide、start_session、create_new_diagram、load_diagram、edit_diagram、screenshot_diagram、export_diagram 等）。
- 交付前把临时 profile、temp vendor 目录清掉；保留最终 tgz 和（如更新了桌面 profile）同步好的 lockfile。
