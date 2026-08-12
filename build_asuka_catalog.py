"""Generate the deterministic Asuka package projection from local mirrors."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml


MAX_NAME_CHARS = 63
MAX_DESCRIPTION_CHARS = 1024
MAX_DOCUMENT_BYTES = 512 * 1024
MAX_PACKAGE_FILES = 256
MAX_MEMBER_BYTES = 5 * 1024 * 1024
MAX_PACKAGE_BYTES = 20 * 1024 * 1024
MAX_PATH_CHARS = 240
MAX_PATH_DEPTH = 8
RESOURCE_DIRECTORIES = ("assets", "references", "scripts")
SKIP_DIRECTORIES = frozenset({".git", ".hg", ".svn", "__pycache__", "node_modules"})
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
logger = logging.getLogger("asuka-catalog-builder")


@dataclass(frozen=True)
class RepositoryIdentity:
    name: str
    root: Path
    url: str
    commit: str


@dataclass(frozen=True)
class Candidate:
    repository: RepositoryIdentity
    source_document: Path
    source_path: str
    original_name: str
    base_name: str
    description: str
    body: str
    frontmatter_keys: tuple[str, ...]


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _slug(value: str, source_path: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    if not normalized:
        normalized = "skill-" + hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:10]
    normalized = re.sub(r"-+", "-", normalized)[:MAX_NAME_CHARS].rstrip("-")
    return normalized or "skill-" + hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:10]


def _frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        raise ValueError("frontmatter_missing")
    match = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.S)
    if match is None:
        raise ValueError("frontmatter_invalid")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("frontmatter_invalid")
    body = text[match.end():]
    if not body.strip():
        raise ValueError("document_body_missing")
    return value, body


def _run_git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=30,
    )
    return completed.stdout.strip()


def _repository_identity(root: Path, repository: str) -> RepositoryIdentity:
    repository_root = root / "repositories" / Path(*repository.split("/"))
    if not repository_root.is_dir() or not (repository_root / ".git").exists():
        raise ValueError("repository_mirror_missing")
    commit = _run_git(repository_root, "rev-parse", "--verify", "HEAD")
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("repository_commit_invalid")
    url = _run_git(repository_root, "remote", "get-url", "origin")
    match = re.fullmatch(
        r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?",
        url,
        re.IGNORECASE,
    )
    if match is None:
        raise ValueError("repository_url_invalid")
    repository_name = match.group(2)
    if repository_name.casefold().endswith(".git"):
        repository_name = repository_name[:-4]
    canonical_url = f"https://github.com/{match.group(1)}/{repository_name}.git"
    return RepositoryIdentity(
        name=repository,
        root=repository_root,
        url=canonical_url,
        commit=commit,
    )


def _candidate(repository: RepositoryIdentity, document: Path) -> Candidate:
    raw = document.read_bytes()
    if not raw or len(raw) > MAX_DOCUMENT_BYTES:
        raise ValueError("document_size_invalid")
    text = raw.decode("utf-8")
    metadata, body = _frontmatter(text)
    source_path = document.relative_to(repository.root).as_posix()
    provenance_path = f"repositories/{repository.name}/{source_path}"
    original_name = str(metadata.get("name") or document.parent.name).strip()
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        description = f"Imported Skill from {repository.name}/{source_path}."
    description = re.sub(r"\s+", " ", description).strip()
    # Asuka 的严格文档合同拒绝尖括号，避免把上游示例标记误解释为 HTML。
    description = description.replace("<", "(").replace(">", ")")[:MAX_DESCRIPTION_CHARS]
    return Candidate(
        repository=repository,
        source_document=document,
        source_path=source_path,
        original_name=original_name,
        base_name=_slug(original_name, provenance_path),
        description=description,
        body=body,
        frontmatter_keys=tuple(sorted(str(key) for key in metadata)),
    )


def _repository_documents(repository: RepositoryIdentity) -> list[Path]:
    documents: list[Path] = []
    for current, directories, files in os.walk(repository.root):
        directories[:] = sorted(item for item in directories if item not in SKIP_DIRECTORIES)
        if "SKILL.md" in files:
            documents.append(Path(current) / "SKILL.md")
    return sorted(
        documents,
        key=lambda item: item.relative_to(repository.root).as_posix().casefold(),
    )


def _catalog_records(root: Path) -> list[dict[str, Any]]:
    value = json.loads((root / "index.json").read_text(encoding="utf-8-sig"))
    skills = value.get("skills") if isinstance(value, dict) else None
    if not isinstance(skills, list):
        raise ValueError("catalog_skills_invalid")
    records: list[dict[str, Any]] = []
    for item in skills:
        if not isinstance(item, dict):
            continue
        repository_id = str(item.get("repository") or "")
        name = str(item.get("name") or "").strip()
        if not repository_id.startswith("github:") or not name:
            continue
        records.append({"repository": repository_id[7:], "name": name})
    return sorted(
        records,
        key=lambda item: (item["repository"].casefold(), item["name"].casefold()),
    )


def _match_candidates(
    repository: RepositoryIdentity,
    catalog_names: Iterable[str],
) -> tuple[list[Candidate], list[dict[str, str]]]:
    rejected: list[dict[str, str]] = []
    candidates: list[Candidate] = []
    for document in _repository_documents(repository):
        try:
            candidates.append(_candidate(repository, document))
        except OSError:
            rejected.append({
                "repository": repository.name,
                "source_path": document.relative_to(repository.root).as_posix(),
                "reason": "document_read_failed",
            })
        except UnicodeError:
            rejected.append({
                "repository": repository.name,
                "source_path": document.relative_to(repository.root).as_posix(),
                "reason": "document_encoding_invalid",
            })
        except yaml.YAMLError:
            rejected.append({
                "repository": repository.name,
                "source_path": document.relative_to(repository.root).as_posix(),
                "reason": "frontmatter_yaml_invalid",
            })
        except ValueError as error:
            rejected.append({
                "repository": repository.name,
                "source_path": document.relative_to(repository.root).as_posix(),
                "reason": str(error) or "document_invalid",
            })

    aliases: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        original_tail = candidate.original_name.rsplit("/", 1)[-1]
        values = {
            candidate.original_name.casefold(),
            original_tail.casefold(),
            candidate.base_name.casefold(),
            _slug(original_tail, candidate.source_path).casefold(),
            _slug(candidate.source_document.parent.name, candidate.source_path).casefold(),
        }
        for value in values:
            aliases.setdefault(value, []).append(candidate)

    matched: dict[str, Candidate] = {}
    content_identities: dict[str, str] = {}
    for catalog_name in sorted(set(catalog_names), key=str.casefold):
        catalog_tail = catalog_name.rsplit("/", 1)[-1]
        keys = {
            catalog_name.casefold(),
            catalog_tail.casefold(),
            _slug(catalog_name, repository.name).casefold(),
            _slug(catalog_tail, repository.name).casefold(),
        }
        options = {
            candidate.source_path: candidate
            for key in keys
            for candidate in aliases.get(key, [])
        }
        if len(options) == 1:
            candidate = next(iter(options.values()))
            matched[candidate.source_path] = candidate
            continue
        if len(options) > 1:
            for candidate in options.values():
                if candidate.source_path not in content_identities:
                    content_identities[candidate.source_path] = hashlib.sha256(
                        _normalized_document(candidate, candidate.base_name)
                    ).hexdigest()
            identities = {
                content_identities[candidate.source_path]
                for candidate in options.values()
            }
            if len(identities) == 1:
                candidate = min(
                    options.values(),
                    key=lambda item: item.source_path.casefold(),
                )
                matched[candidate.source_path] = candidate
                continue
        rejected.append({
            "repository": repository.name,
            "catalog_name": catalog_name,
            "reason": "catalog_skill_ambiguous" if options else "catalog_skill_not_found",
        })
    return list(matched.values()), rejected


def _source_key(candidate: Candidate) -> str:
    return f"{candidate.repository.name}:{candidate.source_path}"


def _source_id(candidate: Candidate) -> str:
    return f"{candidate.repository.name}@{candidate.repository.commit}:{candidate.source_path}"


def _previous_names(output: Path) -> dict[str, str]:
    try:
        value = json.loads((output / "index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    packages = value.get("packages") if isinstance(value, dict) else None
    if not isinstance(packages, list):
        return {}
    result: dict[str, str] = {}
    for item in packages:
        if not isinstance(item, dict):
            continue
        source_key = item.get("source_key")
        name = item.get("name")
        if isinstance(source_key, str) and isinstance(name, str) and NAME_PATTERN.fullmatch(name):
            result[source_key] = name
    return result


def _canonical_names(candidates: list[Candidate], previous: dict[str, str]) -> dict[str, str]:
    names: dict[str, str] = {}
    occupied: set[str] = set()
    ordered = sorted(
        candidates,
        key=lambda item: (item.base_name, item.repository.name.casefold(), item.source_path.casefold()),
    )
    for candidate in ordered:
        source_key = _source_key(candidate)
        old = previous.get(source_key)
        if old and old not in occupied:
            names[source_key] = old
            occupied.add(old)
    for candidate in ordered:
        source_key = _source_key(candidate)
        if source_key in names:
            continue
        canonical = candidate.base_name
        if canonical in occupied:
            suffix = hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:10]
            canonical = f"{canonical[: MAX_NAME_CHARS - 11].rstrip('-')}-{suffix}"
        if canonical in occupied:
            raise RuntimeError("canonical_name_collision")
        names[source_key] = canonical
        occupied.add(canonical)
    return names


def _normalized_document(candidate: Candidate, canonical_name: str) -> bytes:
    frontmatter = yaml.safe_dump(
        {"name": canonical_name, "description": candidate.description},
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).strip()
    return f"---\n{frontmatter}\n---\n{candidate.body.lstrip()}".encode("utf-8")


def _portable_resource_path(path: PurePosixPath) -> bool:
    return bool(
        len(path.as_posix()) <= MAX_PATH_CHARS
        and len(path.parts) <= MAX_PATH_DEPTH
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def _resource_files(candidate: Candidate) -> list[Path]:
    package_root = candidate.source_document.parent
    result: list[Path] = []
    for directory_name in RESOURCE_DIRECTORIES:
        resource_root = package_root / directory_name
        if not resource_root.is_dir() or resource_root.is_symlink():
            continue
        if (resource_root / "SKILL.md").is_file():
            continue
        for current, directories, files in os.walk(resource_root):
            current_path = Path(current)
            directories[:] = sorted(
                item
                for item in directories
                if item not in SKIP_DIRECTORIES
                and not (current_path / item).is_symlink()
                and not (current_path / item / "SKILL.md").is_file()
            )
            for filename in sorted(files):
                source = current_path / filename
                if source.name == "SKILL.md" or source.is_symlink() or not source.is_file():
                    continue
                relative = PurePosixPath(*source.relative_to(package_root).parts)
                if _portable_resource_path(relative):
                    result.append(source)
    return sorted(result, key=lambda path: path.relative_to(package_root).as_posix())


def _package_hash(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative_path in sorted(files):
        path_bytes = relative_path.encode("utf-8")
        content = files[relative_path]
        digest.update(len(path_bytes).to_bytes(4, "big"))
        digest.update(path_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _replace_output(stage: Path, output: Path) -> None:
    backup = output.with_name(f"{output.name}.previous-{os.getpid()}")
    if backup.exists():
        shutil.rmtree(backup)
    if output.exists():
        output.replace(backup)
    try:
        stage.replace(output)
    except Exception:
        if backup.exists() and not output.exists():
            backup.replace(output)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def build(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    output = root / "asuka"
    stage = root / f"asuka.stage-{os.getpid()}"
    if stage.exists():
        shutil.rmtree(stage)
    packages_root = stage / "packages"
    packages_root.mkdir(parents=True)

    records = _catalog_records(root)
    names_by_repository: dict[str, list[str]] = {}
    for record in records:
        names_by_repository.setdefault(record["repository"], []).append(record["name"])

    rejected: list[dict[str, str]] = []
    candidates: list[Candidate] = []
    repository_names = sorted(names_by_repository, key=str.casefold)
    logger.info("Asuka projection discovery started: repositories=%s", len(repository_names))
    for index, repository_name in enumerate(repository_names, start=1):
        try:
            identity = _repository_identity(root, repository_name)
            matched, repository_rejections = _match_candidates(
                identity,
                names_by_repository[repository_name],
            )
            candidates.extend(matched)
            rejected.extend(repository_rejections)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            if isinstance(error, ValueError) and str(error) in {
                "repository_mirror_missing",
                "repository_commit_invalid",
                "repository_url_invalid",
            }:
                reason = str(error)
            elif isinstance(error, subprocess.SubprocessError):
                reason = "repository_git_identity_unavailable"
            else:
                reason = "repository_identity_unavailable"
            rejected.append({
                "repository": repository_name,
                "reason": reason,
            })
        if index % 25 == 0 or index == len(repository_names):
            logger.info(
                "Asuka projection discovery progress: processed=%s total=%s candidates=%s rejected=%s",
                index,
                len(repository_names),
                len(candidates),
                len(rejected),
            )

    previous = _previous_names(output)
    canonical_names = _canonical_names(candidates, previous)
    packages: list[dict[str, Any]] = []
    omissions: list[dict[str, Any]] = []
    for candidate in sorted(
        candidates,
        key=lambda item: (item.repository.name.casefold(), item.source_path.casefold()),
    ):
        source_key = _source_key(candidate)
        source_id = _source_id(candidate)
        name = canonical_names[source_key]
        target = packages_root / name
        target.mkdir()
        document = _normalized_document(candidate, name)
        if len(document) > MAX_DOCUMENT_BYTES:
            rejected.append({
                "repository": candidate.repository.name,
                "source_path": candidate.source_path,
                "reason": "normalized_document_too_large",
            })
            shutil.rmtree(target)
            continue

        file_data = {"SKILL.md": document}
        (target / "SKILL.md").write_bytes(document)
        total_bytes = len(document)
        omitted_paths: list[str] = []
        package_root = candidate.source_document.parent
        for source in _resource_files(candidate):
            relative = source.relative_to(package_root)
            relative_text = PurePosixPath(*relative.parts).as_posix()
            try:
                size = source.stat().st_size
            except OSError:
                omitted_paths.append(relative_text)
                continue
            if (
                size > MAX_MEMBER_BYTES
                or len(file_data) + 1 > MAX_PACKAGE_FILES
                or total_bytes + size > MAX_PACKAGE_BYTES
            ):
                omitted_paths.append(relative_text)
                continue
            try:
                content = source.read_bytes()
            except OSError:
                omitted_paths.append(relative_text)
                continue
            if len(content) != size:
                omitted_paths.append(relative_text)
                continue
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            file_data[relative_text] = content
            total_bytes += size

        package_hash = _package_hash(file_data)
        files = [
            {
                "path": path,
                "size_bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
            for path, content in sorted(file_data.items())
        ]
        if omitted_paths:
            omissions.append({
                "name": name,
                "source_id": source_id,
                "omitted_count": len(omitted_paths),
                "paths": omitted_paths,
            })
        packages.append({
            "name": name,
            "path": f"asuka/packages/{name}",
            "source_key": source_key,
            "source_id": source_id,
            "source_repository": candidate.repository.name,
            "source_repository_url": candidate.repository.url,
            "source_commit": candidate.repository.commit,
            "source_path": candidate.source_path,
            "original_name": candidate.original_name,
            "original_frontmatter_keys": list(candidate.frontmatter_keys),
            "document_sha256": hashlib.sha256(document).hexdigest(),
            "package_hash": package_hash,
            "file_count": len(files),
            "total_bytes": total_bytes,
            "files": files,
        })

    packages.sort(key=lambda item: item["name"])
    rejected.sort(
        key=lambda item: (
            item.get("repository", "").casefold(),
            item.get("catalog_name", "").casefold(),
            item.get("source_path", "").casefold(),
            item.get("reason", ""),
        )
    )
    omissions.sort(key=lambda item: item["name"])
    index = {
        "schema_version": 1,
        "package_count": len(packages),
        "rejected_count": len(rejected),
        "resource_omission_count": len(omissions),
        "limits": {
            "max_document_bytes": MAX_DOCUMENT_BYTES,
            "max_package_files": MAX_PACKAGE_FILES,
            "max_member_bytes": MAX_MEMBER_BYTES,
            "max_package_bytes": MAX_PACKAGE_BYTES,
            "max_path_chars": MAX_PATH_CHARS,
            "max_path_depth": MAX_PATH_DEPTH,
        },
        "packages": packages,
    }
    _atomic_json(stage / "index.json", index)
    _atomic_json(stage / "rejected.json", {"items": rejected})
    _atomic_json(stage / "resource-omissions.json", {"items": omissions})
    _replace_output(stage, output)
    logger.info(
        "Asuka projection build completed: packages=%s rejected=%s omissions=%s",
        len(packages),
        len(rejected),
        len(omissions),
    )
    return index


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    result = build(args.root)
    print(json.dumps({key: result[key] for key in (
        "schema_version", "package_count", "rejected_count", "resource_omission_count"
    )}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
