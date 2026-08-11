# Skill repository mirror

This directory mirrors skills from both catalogs:

- `https://github.com/anbeime/skill/blob/main/data/skills.json`
- `https://www.skills.sh/official`

Run a sync manually:

```text
python sync_skills.py
```

The default GitHub proxy is `socks5h://127.0.0.1:10808`. Override it with
`--proxy socks5h://HOST:PORT` (or `http://HOST:PORT` for an HTTP proxy), or
disable it explicitly with `--no-proxy`.

Register the current-user Python background loop:

```text
python register_autostart.py --daily-at 03:00
```

The sync process refreshes both catalogs, merges repositories by case-insensitive `owner/repo`, clones newly listed repositories, and runs `git pull --ff-only --prune` for existing repositories. New repositories use shallow partial clones and sparse checkout so only directories containing `SKILL.md` are materialized. Repositories that were already cloned in full remain full clones.

Layout:

- `repositories/<owner>/<repository>` contains one Git repository per unique source.
- `external/` contains snapshots for non-Git sources from the JSON catalog.
- `state/skills.json` is the latest JSON catalog.
- `state/official.json` is the normalized official catalog from skills.sh.
- `state/repositories.json` maps repositories to catalog sources and skills.
- `state/last-run.json` contains the latest result for every source.
- `logs/` contains timestamped sync logs and the background-loop log.
- `repository-overrides.json` maps removed repositories to verified public mirrors.

The background loop is launched by the current user's Windows startup registry entry through `pythonw.exe`. It runs at 03:00 local time, catches up after sleep or a missed run, retries failures up to three times at 15-minute intervals, and uses Windows mutexes to prevent duplicate loops or overlapping manual syncs.

Local changes are never reset. A pull that cannot fast-forward is recorded as failed for manual inspection. Catalog repositories that return GitHub's `Repository not found` response are recorded as `Unavailable` and checked again on every run.
