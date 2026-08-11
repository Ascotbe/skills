# GitHub Growth & Discoverability Checklist

This guide collects the **off-repo** settings that drive GitHub search ranking,
Google indexing, and star conversion. The README and docs are optimized in-repo;
the items below are set on the GitHub website (not in this repository).

> Repo: `https://github.com/huifer/WellAlly-health`

---

## 1. Repository "About" Description

The About section appears next to the README and is a major SEO signal. Keep it
under ~350 characters and lead with the highest-value keywords.

**English (recommended):**
```
WellAlly Health — a privacy-first, local-only personal health record (PHR) system.
AI-powered medical report recognition, drug-interaction checks, and 16-specialty
MDT analysis. 62 commands, 20 skills, zero cloud.
```

**中文（备选）：**
```
WellAlly Health — 隐私优先、纯本地的个人健康档案（PHR）系统。AI 识别医疗报告、
药物冲突检测、16 专科多学科会诊。62 命令、20 技能、零上云。
```

Tips:
- Put the keyword **personal health record / PHR** and **privacy-first** early.
- Mention the differentiator: **local-only / no cloud**.
- Add the homepage link `https://www.wellally.tech` and pick a topic color.

---

## 2. Topics (up to 20)

Topics power GitHub's topic pages and "related repositories" surfacing. Use a
mix of high-volume and niche terms:

```
personal-health-record
phr
medical-records
health-tracking
health-management
privacy
local-first
ai-health
claude
claude-code
drug-interaction
health-analytics
medical-image-analysis
traditional-chinese-medicine
wellness
healthcare
personal-data
self-hosted
open-source
data-privacy
```

Priority order: the first ~10 carry the most weight. Rotate based on which
topics actually drive traffic (check GitHub Insights → Traffic).

---

## 3. Social Preview Image

GitHub auto-generates a bland preview when no image is set. A branded 1280×640
image dramatically improves click-through from Slack, Twitter/X, Hacker News,
and Reddit shares.

- Size: **1280 × 640 px** (2:1)
- Content: project name "WellAlly Health", tagline "Privacy-first personal
  health intelligence", and 2–3 hero keywords (Local-only · AI-powered ·
  Drug-interaction).
- Set at: **Settings → General → Social preview**.
- Note: visual assets are intentionally deferred for this pass; generate when
  convenient (the repo currently ships no logo).

---

## 4. Releases & Tags

- Cut a tagged release `v2.0.0` (and increment going forward). Releases appear
  in the GitHub release feed and are indexed.
- Write each release notes from `CHANGELOG.md`.
- Pin a stable default branch (`main`).

---

## 5. Community Health Files

Already present / added in this optimization:

- ✅ `README.md` + `README.zh-CN.md` (rewritten, SEO-friendly)
- ✅ `CONTRIBUTING.md` / `CONTRIBUTING.en.md`
- ✅ `CODE_OF_CONDUCT.md` (new)
- ✅ `SECURITY.md` / `SECURITY.en.md`
- ✅ `CHANGELOG.md` (new)
- ✅ Issue templates (`bug_report.md`, `feature_request.md`)
- ✅ `PULL_REQUEST_TEMPLATE.md`
- ⬜ `FUNDING.yml` — optional; add `.github/FUNDING.yml` to enable the Sponsor
  button (GitHub Sponsors / custom URL).

Enable **Discussions** (Settings → General → Features) so the README's
Discussions link resolves.

---

## 6. Discovery & Growth Checklist

- [ ] Set the About description (§1) and Topics (§2) on github.com
- [ ] Upload a 1280×640 social preview image (§3)
- [ ] Cut and publish release `v2.0.0`
- [ ] Enable Discussions
- [ ] Add `good first issue` and `help wanted` labels; tag 3–5 starter issues
- [ ] Pin a welcoming issue / discussion (e.g. "Welcome to WellAlly Health 👋")
- [ ] Submit to relevant directories: awesome-selfhosted, awesomelists, etc.
- [ ] Share the launch post (see `docs/marketing/`) on Hacker News, Reddit
      (r/selfhosted, r/privacy), V2EX, and dev communities — all links now
      point to the correct repo `huifer/WellAlly-health`
- [ ] Monitor Insights → Traffic and adjust Topics monthly
