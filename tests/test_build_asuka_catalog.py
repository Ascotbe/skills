from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_asuka_catalog import build


def _git(repository: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )


def _repository(root: Path, name: str, documents: dict[str, str]) -> Path:
    target = root / "repositories" / Path(*name.split("/"))
    target.mkdir(parents=True)
    _git(target, "init")
    _git(target, "config", "user.email", "tests@example.invalid")
    _git(target, "config", "user.name", "Catalog Tests")
    _git(target, "remote", "add", "origin", f"https://github.com/{name}.git")
    for relative_path, content in documents.items():
        path = target / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _git(target, "add", ".")
    _git(target, "commit", "-m", "fixture")
    return target


def _catalog(root: Path, skills: list[tuple[str, str]]) -> None:
    root.joinpath("index.json").write_text(
        json.dumps({
            "skills": [
                {"repository": f"github:{repository}", "name": name}
                for repository, name in skills
            ]
        }),
        encoding="utf-8",
    )


def test_build_normalizes_frontmatter_and_copies_bounded_resources(tmp_path: Path) -> None:
    repository = _repository(
        tmp_path,
        "acme/skills",
        {
            "skills/Deploy/SKILL.md": (
                "---\nname: Deploy Service\ndescription: Ship the service.\n"
                "homepage: https://example.invalid\nmetadata:\n  owner: acme\n---\n"
                "# Deploy\n\nUse the release workflow.\n"
            ),
            "skills/Deploy/scripts/run.ps1": "Write-Output 'ok'\n",
        },
    )
    _git(repository, "add", ".")
    _git(repository, "commit", "--allow-empty", "-m", "resources")
    _catalog(tmp_path, [("acme/skills", "Deploy Service")])

    result = build(tmp_path)

    assert result["package_count"] == 1
    package = result["packages"][0]
    assert package["name"] == "deploy-service"
    assert package["source_key"] == "acme/skills:skills/Deploy/SKILL.md"
    assert package["source_commit"] == _git_output(repository, "rev-parse", "HEAD")
    skill_path = tmp_path / package["path"] / "SKILL.md"
    metadata = yaml.safe_load(skill_path.read_text(encoding="utf-8").split("---", 2)[1])
    assert metadata == {"name": "deploy-service", "description": "Ship the service."}
    assert (skill_path.parent / "scripts" / "run.ps1").is_file()
    assert package["package_hash"] == _package_hash(skill_path.parent)


def _git_output(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _package_hash(root: Path) -> str:
    digest = hashlib.sha256()
    files = {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
    }
    for relative_path in sorted(files):
        path = files[relative_path]
        relative = relative_path.encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def test_build_rejects_missing_and_ambiguous_catalog_names(tmp_path: Path) -> None:
    _repository(
        tmp_path,
        "acme/skills",
        {
            "one/SKILL.md": "---\nname: shared\ndescription: One.\n---\n# One\n",
            "two/SKILL.md": "---\nname: shared\ndescription: Two.\n---\n# Two\n",
        },
    )
    _catalog(tmp_path, [("acme/skills", "shared"), ("acme/skills", "missing")])

    result = build(tmp_path)

    assert result["package_count"] == 0
    reasons = {
        item["reason"]
        for item in json.loads(
            (tmp_path / "asuka" / "rejected.json").read_text(encoding="utf-8")
        )["items"]
    }
    assert reasons == {"catalog_skill_ambiguous", "catalog_skill_not_found"}


def test_rebuild_is_deterministic_and_keeps_previous_name(tmp_path: Path) -> None:
    repository = _repository(
        tmp_path,
        "acme/skills",
        {"one/SKILL.md": "---\nname: stable\ndescription: Stable.\n---\n# Stable\n"},
    )
    _catalog(tmp_path, [("acme/skills", "stable")])
    first = build(tmp_path)
    first_bytes = (tmp_path / "asuka" / "index.json").read_bytes()

    second = build(tmp_path)

    assert first == second
    assert (tmp_path / "asuka" / "index.json").read_bytes() == first_bytes
    assert second["packages"][0]["source_commit"] == _git_output(repository, "rev-parse", "HEAD")


def test_owner_alias_and_identical_repository_copies_are_deduplicated(
    tmp_path: Path,
) -> None:
    document = "---\nname: shared\ndescription: Shared.\n---\n# Shared\n"
    _repository(
        tmp_path,
        "acme/skills",
        {
            "plugins/one/skills/shared/SKILL.md": document,
            "plugins/two/skills/shared/SKILL.md": document,
        },
    )
    _catalog(tmp_path, [("acme/skills", "acme/shared")])

    result = build(tmp_path)

    assert result["package_count"] == 1
    assert result["packages"][0]["name"] == "shared"
    assert result["packages"][0]["source_path"] == (
        "plugins/one/skills/shared/SKILL.md"
    )


def test_projection_disables_git_text_conversion() -> None:
    """发布投影必须保留生成器计算 hash 时使用的原始字节。"""
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "check-attr",
            "text",
            "--",
            "asuka/packages/example/SKILL.md",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip().endswith("text: unset")
