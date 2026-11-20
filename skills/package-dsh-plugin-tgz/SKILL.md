---
name: package-dsh-plugin-tgz
description: Package a DeepSeek Harness (DSH) plugin source folder into a single offline-installable .tgz using dist-packages/pack-plugin.cmd. Use this whenever the user wants to 打包/离线打包 a DSH plugin, make an offline tgz, bundle a plugin's runtime dependencies into a tarball, or prepare a plugin for offline install — even if they just say "pack this plugin" or "make a tgz for offline". It handles regular plugins whose deps are plain npm deps, and correctly skips host-provided peer deps (react, @deepseek-ai/cordis, @deepseek-ai/dsh-*).
compatibility: Windows, Node.js/npm on PATH, cmd.exe. Script lives at dist-packages/pack-plugin.cmd in the workspace and is also bundled in this skill's scripts/.
---

# 打包离线 DSH 插件 tgz

把一个 DSH 插件源码目录打成一个**可离线安装的 `.tgz`**：运行时依赖（普通 npm `dependencies`）会随 `node_modules` 内联进包里，宿主自带的依赖（`peerDependencies` 里的 `react`/`react-dom`/`@deepseek-ai/cordis`/`@deepseek-ai/dsh-*`）不会重复打包。

## 何时用

- 用户说“打包插件 / 离线打包 / 打个 tgz / 做成离线包 / pack this plugin / offline tgz”。
- 目标是一个 DSH 插件仓库（含 `package.json`），要拿去离线安装或分发。
- **不适用**：纯前端静态资源压缩成伪 `.txt`（那是 `zip-to-txt.py` 的事）；npm 发包到 registry（那是 CI/release 流程）。

## 打包脚本

主脚本：`dist-packages\pack-plugin.cmd`（本技能也在 `scripts/pack-plugin.cmd` 放了一份副本，可复制到任意机器独立使用）。

工作区里脚本通常位于 `<工作区>\dist-packages\pack-plugin.cmd`。请用你本机实际的工作区路径替换下文示例中的 `C:\path\to\workspace`。

运行它的标准姿势是**先 `cd` 进插件根目录**，再调用脚本；默认就地产出 `<name>-<version>-bundled.tgz`：

```cmd
cd C:\path\to\workspace\repos\dsh-mnemon
C:\path\to\workspace\dist-packages\pack-plugin.cmd
```

也可以用 `-Repo` 直接指定目录、用 `-Out` 指定输出目录，不必切换当前目录：

```cmd
pack-plugin.cmd -Repo C:\path\to\plugin -Out D:\pkgs
```

## 工作流

1. **确认目标目录**：找到插件根目录（有 `package.json` 的那一层）。源码通常在工作区 `repos/` 下；如果打包的是已安装插件，源码一般在工作区同名目录或 `repos/`。
2. **读 `package.json`**，判断依赖类型，决定要不要显式列依赖：
   - `dependencies` 里**非** `@deepseek-ai/dsh*`、非 `@deepseek-ai/cordis`、不在 `peerDependencies` 里的，脚本会**自动**内联，无需手写。
   - 只想内联其中几个，就在命令后列出名字（或 `-Deps a,b`）。
   - 没有运行时依赖的纯 cordis-patch 插件（如 `next-ai-drawio/dsh`）直接打，出的包本身就是离线可装的。
3. **选参数**（完整表见 `references/pack-plugin-opts.md`）：
   - 插件需要先编译：`-Build`（跑 `npm run build --if-present`）。
   - 已有 `node_modules` 且确认可用：`-NoInstall` 跳过安装（最快）。
   - 依赖装歪了要重装：`-ForceInstall`。
   - 想保留 `bundleDependencies` 在 `package.json` 里：`-NoRestore`。
4. **执行打包**（用 `cmd /c`，PowerShell 里不要直接跑 .cmd；见下面 Windows 坑）。
5. **读输出**：成功后打印 tarball 路径、size、files、sha256，并给出安装命令。
6. **校验**（脚本已内置，但交付前可人工复核）：
   - 有内联依赖时脚本会打印 `verified N bundled deps + inlined node_modules`。
   - 可 `tar -tzf <tgz>` 看内容，确认 `package/node_modules/` 存在。
7. **告知安装方式**：
   - 在线：`dsh plugin --profile desktop add "<tgz>"`
   - 离线（有内联依赖）：`install-plugin.cmd "<tgz>"`

## Windows / PowerShell 坑（务必遵守）

- **用 `cmd /c` 调用 .cmd**，不要在 PowerShell 里直接 `& .\pack-plugin.cmd` 然后把 stdout 用 `for/f` 解析——脚本内部已刻意避开 `for/f` 读 npm 输出（`ERRORLEVEL` 会被 `for/f` 清零，导致打包失败被漏报）。
- **路径带空格一定要加引号**；`-Repo`/`-Out` 后的路径脚本会做 `%%~fI` 补全。
- **不要在 PowerShell 里用 `Set-Content`/`-replace` 重写含中文的源文件或 `package.json`**——会把 UTF-8 中文变成 mojibake。要改文件内容用 `edit` 工具做字面替换。
- 脚本要求 `node`、`npm`、`tar`、`certutil` 在 PATH 上（Windows 自带 `tar`/`certutil`）。
- **node_modules 必须是 npm 真实安装过的**：手写/拼凑的 `node_modules` 会让 `npm pack` 报 `errno -4094 / UNKNOWN: unknown error, open ...`。先让脚本自己跑一次 `npm install`（默认就会做），或 `-NoInstall` 前确认依赖是真装过的。
- 出错时脚本会**自动还原 `package.json`**（删掉临时写入的 `bundleDependencies`），并打印 npm pack 日志、以 exit 1 结束；不会留下坏 tgz。放心重试。

## 产物命名规则

`<name>-<version>-bundled.tgz`，其中 scoped 名里的 `@` 被去掉、`/` 变成 `-`（例如 `@next-ai-drawio/dsh` → `next-ai-drawio-dsh-0.1.0-bundled.tgz`），保证 Windows 文件名安全。

## 快速参考

| 目标 | 命令 |
|------|------|
| 打当前插件（自动内联所有非宿主依赖） | `cd <plugin> && pack-plugin.cmd` |
| 指定目录和输出位置 | `pack-plugin.cmd -Repo <dir> -Out <dir>` |
| 先构建再打包 | `pack-plugin.cmd -Build` |
| 已有 node_modules，跳过安装 | `pack-plugin.cmd -NoInstall` |
| 只内联指定依赖 | `pack-plugin.cmd ws yaml` 或 `-Deps ws,yaml` |
| 查看帮助 | `pack-plugin.cmd -h` |

完整参数与边界情况见 `references/pack-plugin-opts.md`。
