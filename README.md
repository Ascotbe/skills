# 技能仓库镜像

本目录用于镜像两个技能目录：

- `https://github.com/anbeime/skill/blob/main/data/skills.json`
- `https://www.skills.sh/official`

## 手动同步

```text
python sync_skills.py
```

默认 GitHub 代理为 `socks5h://127.0.0.1:10808`。可以使用
`--proxy socks5h://HOST:PORT`（HTTP 代理使用 `http://HOST:PORT`），或使用
`--no-proxy` 明确关闭代理。

## 自动同步

注册当前用户的 Python 后台循环：

```text
python register_autostart.py --daily-at 03:00
```

后台循环每天在本地时间 03:00 执行；如果电脑休眠、关机或错过执行时间，会在下次启动时补跑。失败时最多每隔 15 分钟重试三次。Windows 互斥锁会避免重复启动后台循环，也会避免手动同步与自动同步同时运行。

## 目录结构

- `index.json`：根目录索引，包含仓库摘要和技能明细，只保存索引字段、时间和数据文件路径，不重复保存完整目录数据。
- `repositories/<owner>/<repository>`：按来源保存 Git 仓库。
- `external/`：保存 JSON 目录中非 Git 来源的快照。
- `state/skills.json`：最新的 GitHub 技能目录数据。
- `state/official.json`：从 skills.sh 规范化得到的目录数据。
- `state/repositories.json`：仓库与目录来源、技能的对应关系。
- `state/external-links.json`：非 Git 来源条目。
- `state/last-run.json`：最近一次同步的结果。
- `logs/`：按时间命名的同步日志和后台循环日志。
- `repository-overrides.json`：将已移除的仓库映射到经过验证的公开镜像。

## 索引时间字段

`index.json` 中每个条目都有：

- `added_at`：条目首次加入本地索引的时间。后续同步会保留该值。
- `updated_at`：条目最近一次成功拉取或下载的时间。同步失败或仓库不可用时不会更新该值。

索引顶层的 `entries` 用于按仓库或外部来源导航，`skills` 用于按技能检索；两者都使用稳定的 `id`，并分别记录加入时间和更新时间。

时间使用带时区的 ISO 8601 格式。仓库条目和外部快照条目使用稳定的 `id`，因此目录顺序变化不会丢失历史时间。

## 同步行为

同步过程会刷新两个目录源，按不区分大小写的 `owner/repository` 合并仓库，克隆新仓库，并对已有仓库执行 `git pull --ff-only --prune`。新仓库使用浅层部分克隆和稀疏检出，只物化包含 `SKILL.md` 的目录；已经完整克隆的仓库保持完整检出。

本地修改不会被重置。无法快进的拉取会记录为失败，供人工检查。目录中返回 GitHub “Repository not found” 的仓库会标记为 `Unavailable`，并在每次同步时重新检查。
