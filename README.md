# Asuka 官方 Skill 镜像

> 私有项目 **Asuka** 的官方 Skill 镜像与分发源。

本仓库集中收集公开发布的 Skill，为 Asuka Assistant V2 提供可检索、可追踪的候选内容。它不是面向任意助理机器人的通用技能市场，也不保存 Asuka 的私有源码、用户数据、运行凭据或任务上下文。上游仓库只在同步机器本地下载，不提交到本仓库。

| 项目 | 说明 |
| --- | --- |
| 使用方 | 私有项目 Asuka |
| 仓库身份 | `github.com/ascotbe/skills` |
| 主要用途 | 官方 Skill 候选的镜像、索引与分发 |
| 信任方式 | 仓库身份、Git commit、相对路径和 package hash |
| 异常策略 | 校验失败即拒绝，并继续使用上一版可用数据 |

## 数据来源

当前聚合以下公开目录：

- `https://github.com/anbeime/skill/blob/main/data/skills.json`
- `https://www.skills.sh/official`

本仓库只同步公开可访问的内容，不绕过访问控制。镜像收录不代表内容已经通过 Asuka 校验，也不会替代上游许可证。使用者仍须遵守各上游仓库或 Skill 自身的许可证、版权要求和服务条款。

## Asuka 接入流程

Asuka 在代码中将本仓库固定为官方 Skill 仓库身份和信任根，不允许通过普通环境变量或客户端请求替换。

```text
公开上游目录
    -> 本地同步、去重并建立 index.json
    -> 生成 asuka/ 下的严格兼容 package 投影
    -> Asuka 固定远端仓库身份与 Git commit
    -> 从受版本控制的 SKILL.md 发现 package
    -> 校验路径、文件类型、大小、格式与内容哈希
    -> 校验 Skill package 合同
    -> 通过后进入 Asuka 官方 Skill Catalog
```

同步失败时，Asuka 不会发布不完整内容，而是继续使用上一版可用数据。

## 安全边界

- `index.json` 仅用于检索与追溯，不是授权结果或执行证明。
- 只有具备完整仓库证明且通过 Asuka 校验的内容，才能成为官方 Skill。
- Asuka 对不可信仓库内容采用失败即关闭策略，异常内容不会被提升为官方 Skill。
- Skill 被发现、同步或展示，不代表它已被任务选中或实际执行。
- 实际调用以 Asuka 的结构化运行事件和操作回执为准。

## 索引结构

根目录的 `index.json` 是轻量索引，不重复保存完整目录数据：

| 字段 | 作用 |
| --- | --- |
| `entries` | 按仓库或外部来源导航 |
| `skills` | 按 Skill 检索 |
| `data` | 指向 `state/` 下的详细数据文件 |
| `added_at` | 首次加入索引的时间，后续同步保持不变 |
| `updated_at` | 最近一次成功同步时间；失败或不可用时不刷新 |

仓库与 Skill 均使用稳定 `id`。时间采用带时区的 ISO 8601 格式，因此目录顺序变化不会丢失历史时间。

## 同步方式

### 手动同步

```text
python sync_skills.py
```

默认 GitHub 代理为 `socks5h://127.0.0.1:10808`：

```text
python sync_skills.py --proxy socks5h://HOST:PORT
python sync_skills.py --proxy http://HOST:PORT
python sync_skills.py --no-proxy
```

### 自动同步

注册当前用户的后台循环，每天本地时间 03:00 执行：

```text
python register_autostart.py --daily-at 03:00
```

错过计划时间时会在下次启动后补跑。失败任务最多每隔 15 分钟重试三次；Windows 互斥锁用于防止后台循环重复启动，以及自动同步和手动同步重叠运行。

## 同步规则

- 刷新两个目录源，并按不区分大小写的 `owner/repository` 合并仓库。
- 新仓库使用浅层部分克隆和稀疏检出，只物化包含 `SKILL.md` 的目录。
- 已有仓库执行 `git pull --ff-only --prune`；原本为完整检出的仓库保持完整检出。
- 本地修改不会被重置，无法快进的拉取会记录为失败并等待人工检查。
- GitHub 返回 `Repository not found` 的仓库标记为 `Unavailable`，后续同步仍会重新检查。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| `asuka/index.json` | Asuka package 数量、来源 commit、路径和内容哈希 |
| `asuka/packages/<name>` | 可由 Asuka 运行时下载并严格校验的 package |
| `asuka/rejected.json` | 无法唯一定位或不符合发布边界的候选 |
| `asuka/resource-omissions.json` | 因单包安全上限未纳入的资源 |
| `repositories/<owner>/<repository>` | 本地 Git 镜像，不进入版本控制 |
| `index.json`、`external/`、`state/`、`logs/` | 本地索引、快照、运行状态和日志，不进入版本控制 |
| `repository-overrides.json` | 已移除仓库到已验证公开镜像的映射 |

同步结束会自动执行 `build_asuka_catalog.py`。生成器只收录根 Catalog 能在对应仓库唯一定位的 `SKILL.md`，把 frontmatter 规范为 `name` 与 `description`，并只复制 `scripts/`、`references/`、`assets/` 标准资源。每个 package 都记录固定上游 commit、原路径、成员 hash 和整包 hash；任何超限资源都会显式进入遗漏清单。
