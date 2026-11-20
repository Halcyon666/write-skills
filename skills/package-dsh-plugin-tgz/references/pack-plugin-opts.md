# pack-plugin.cmd 完整参数与机制参考

脚本位置（工作区）：`<工作区>\dist-packages\pack-plugin.cmd`
本技能副本：`scripts/pack-plugin.cmd`（内容一致，可复制到任意机器独立使用）。

## 它到底做什么

对一个插件目录执行以下流程，产出一个**离线可安装**的 tgz：

1. 可选：在插件目录跑 `npm run build --if-present`。
2. `npm install --omit=dev --ignore-scripts --no-audit --no-fund --legacy-peer-deps` —— 只装运行时依赖，且仅当 `node_modules` 不存在时（除非 `-ForceInstall`）。`--legacy-peer-deps` 是必要的：很多插件的 `peerOptional` 指向宿主版本（如 `@deepseek-ai/dsh-client-locale`），普通 `npm install` 会先 ERESOLVE 失败。
3. 备份 `package.json` → `npm pkg delete bundleDependencies` → 逐个写入要内联的 `bundleDependencies[i]`。
4. `npm pack --ignore-scripts --pack-destination <临时目录>`。刻意**不用** `for/f` 抓 npm stdout（`for/f` 之后 ERRORLEVEL 恒为 0，会漏报失败），而是读 ERRORLEVEL、再从临时目录里找实际生成的 `.tgz`。
5. **离线可装校验**：若有内联依赖，检查 tgz 里的 `package/package.json` 有非空 `bundleDependencies`，且包内存在 `package/node_modules/`。任一不满足 → 报错、不移动 tgz、以 exit 1 结束。
6. 还原 `package.json`（或 `-NoRestore` 保留），把 tgz 移到输出目录并按规则改名，再 `tar -tzf` 验完整、`certutil` 算 SHA256、打印报告。

任何失败分支都会先还原 `package.json`，绝不留下坏 tgz。

## 哪些依赖会被内联

默认（`dependencies` 中满足以下**全部**条件的才内联）：

- 名字以 `@deepseek-ai/dsh` 开头 → **不内联**（宿主提供）。
- `@deepseek-ai/cordis` → **不内联**（宿主提供）。
- 出现在 `peerDependencies` 里的（如 `react`、`react-dom`、`@deepseek-ai/dsh-app-boot` 等）→ **不内联**（宿主提供）。
- 其余普通依赖 → **内联**，包括 0.28.x 里作为普通 dependency 的 `@deepseek-ai/schemastery`。

显式列出依赖名时（命令后直接跟名字，或用 `-Deps`），只内联列出的那些，覆盖默认推断。

## 参数表

| 参数 | 作用 |
|------|------|
| `-Repo <dir>` | 打包指定目录，而不是当前 `cd` 的目录 |
| `-Out <dir>` | 输出目录（默认当前目录）；不存在会自动创建 |
| `-Deps a,b,c` | 要内联的依赖，逗号或空格分隔，等价于命令后直接列名字 |
| `-Build` | 打包前跑 `npm run build --if-present` |
| `-NoInstall` | 绝不跑 `npm install`（要求 `node_modules` 已是真实安装状态） |
| `-ForceInstall` | 即使 `node_modules` 存在也强制重装 |
| `-NoRestore` | 打包后不还原 `package.json`，保留写入的 `bundleDependencies` |
| `-?` / `-h` / `--help` | 打印帮助 |

位置参数：命令后任何未被识别为选项的参数都被当作依赖名加入内联集合（逗号会被转成空格）。

## 产物命名

`<name>-<version>-bundled.tgz`，做两处替换让 Windows 文件名安全：

- 去掉 `@`（`!FINAL: @ =!`）
- `/` → `-`（如 `@next-ai-drawio/dsh` → `next-ai-drawio-dsh-0.1.0-bundled.tgz`）

## 报告与安装命令

成功输出示例（依赖包）：

```
==> done
    tarball ...\dsh-test-dep-0.0.2-bundled.tgz
    size    3505 bytes
    files   8
    sha256  73a7085e29e14ee4b5c56b75798f7f01d3b7d39bea1f6a8fde06e75d81cca383

  online install:
    dsh plugin --profile desktop add "<tgz>"
  offline install:
    install-plugin.cmd "<tgz>"
```

无运行时依赖的插件（如 `next-ai-drawio/dsh`）没有 `offline install` 一行——纯文件 tgz 本就离线可装。注意这**只保证可离线安装**：如果插件的 `cordis.patch.yml` 用 `npx ...@latest` 启动服务，运行时仍会联网下载。配置型 MCP bundle 必须按 `references/offline-runtime-audit.md` 做运行时自包含审计并把服务 vendor 进包。

## 典型例子

```cmd
:: 1) 打当前插件（自动内联所有非宿主依赖）
cd C:\path\to\workspace\repos\dsh-mnemon
pack-plugin.cmd

:: 2) 只内联 ws 和 yaml
pack-plugin.cmd ws yaml
pack-plugin.cmd -Deps ws,yaml

:: 3) 指定仓库与输出目录，先构建
pack-plugin.cmd -Repo C:\path\to\plugin -Out D:\pkgs -Build

:: 4) 已有可用的 node_modules，跳过安装
pack-plugin.cmd -NoInstall

:: 5) 依赖装歪了，强制重装
pack-plugin.cmd -ForceInstall
```

## 故障排查

| 现象 | 原因 / 处理 |
|------|-------------|
| `[!] "...\package.json" has no package.json` | `-Repo` 指到了子目录而非插件根；指到含 `package.json` 的那一层 |
| `npm error ... errno -4094 / UNKNOWN: unknown error, open ...\node_modules\...` | `node_modules` 是手写/拼凑的，不是 npm 真装的。去掉 `-NoInstall` 让它重装，或先删 node_modules 再跑 |
| `ERESOLVE` | 脚本已带 `--legacy-peer-deps`；若仍出现，检查 `package.json` 的 peer 版本约束 |
| `[!] tarball has no bundleDependencies` / `no inlined node_modules` | 依赖没被真正内联；确认依赖在 `dependencies` 且不在 `peerDependencies`，必要时显式 `-Deps` |
| `[!] pack failed - no tarball was produced` | 看脚本打印的 npm pack 日志；`package.json` 已被自动还原，修完重跑 |
| PowerShell 里中文文件名/内容乱码 | 别用 `Set-Content`/`-replace` 改含中文的源文件；用 `edit` 工具。调用脚本用 `cmd /c` |
