from __future__ import annotations

import atexit
import argparse
import concurrent.futures
import ctypes
import dataclasses
import datetime as dt
import json
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any

from build_asuka_catalog import build as build_asuka_catalog


DEFAULT_MANIFEST_URL = (
    "https://raw.githubusercontent.com/anbeime/skill/main/data/skills.json"
)
DEFAULT_OFFICIAL_URL = "https://www.skills.sh/official"
DEFAULT_PROXY_URL = "socks5h://127.0.0.1:10808"
GITHUB_CONNECTIVITY_URL = "https://github.com/git/git.git"
USER_AGENT = "skill-repository-sync/2.0"
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
CLONE_TEMP_PATTERN = re.compile(r"\.cloning-\d+-[0-9a-f]+$")
ERROR_ALREADY_EXISTS = 183
SYNC_MUTEX_NAME = "Local\\SkillRepositoriesSyncOperation"
INDEX_SCHEMA_VERSION = 1


@dataclasses.dataclass
class CommandResult:
    returncode: int
    output: str


@dataclasses.dataclass
class RepositoryResult:
    type: str
    name: str
    status: str
    detail: str | None
    local_path: str
    checkout_mode: str | None = None
    skill_file_count: int | None = None
    skipped_skill_file_count: int | None = None


@dataclasses.dataclass
class SyncContext:
    repository_root: Path
    git_executable: str
    retries: int
    git_timeout: int
    proxy_url: str | None
    logger: logging.Logger


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.scripts: list[str] = []
        self._inside_script = False
        self._parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag.casefold() == "script":
            self._inside_script = True
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._inside_script:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "script" and self._inside_script:
            self.scripts.append("".join(self._parts))
            self._inside_script = False
            self._parts = []


def parse_args() -> argparse.Namespace:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Mirror and update repositories listed by the skill catalogs."
    )
    parser.add_argument("--manifest-url", default=DEFAULT_MANIFEST_URL)
    parser.add_argument("--official-url", default=DEFAULT_OFFICIAL_URL)
    parser.add_argument("--proxy", type=parse_proxy_url, default=DEFAULT_PROXY_URL)
    parser.add_argument("--no-proxy", action="store_const", const=None, dest="proxy")
    parser.add_argument("--repository-root", type=Path, default=base / "repositories")
    parser.add_argument("--external-root", type=Path, default=base / "external")
    parser.add_argument("--state-root", type=Path, default=base / "state")
    parser.add_argument("--log-root", type=Path, default=base / "logs")
    parser.add_argument("--index-path", type=Path, default=base / "index.json")
    parser.add_argument(
        "--overrides", type=Path, default=base / "repository-overrides.json"
    )
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--source-timeout", type=int, default=60)
    parser.add_argument("--git-timeout", type=int, default=300)
    args = parser.parse_args()
    if not 1 <= args.workers <= 32:
        parser.error("--workers must be between 1 and 32")
    if not 1 <= args.retries <= 10:
        parser.error("--retries must be between 1 and 10")
    return args


def parse_proxy_url(value: str) -> str:
    value = value.strip()
    if "://" not in value:
        value = f"socks5h://{value}"
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme.casefold() not in {"http", "https", "socks5", "socks5h"}:
        raise argparse.ArgumentTypeError(
            "proxy scheme must be http, https, socks5, or socks5h"
        )
    if not parsed.hostname or parsed.port is None:
        raise argparse.ArgumentTypeError("proxy must include a host and port")
    return value


def setup_logging(log_root: Path) -> tuple[logging.Logger, Path]:
    log_root.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    log_path = log_root / f"sync-{timestamp}.log"
    logger = logging.getLogger("skill-sync")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if sys.stdout is not None:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger, log_path


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(content)
    os.replace(temporary, path)


def atomic_write_json(path: Path, value: Any) -> None:
    content = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
    atomic_write_bytes(path, content)


def load_index(path: Path) -> tuple[dict[str, dict[str, Any]], bool]:
    """Load the existing root index, retaining timestamps across syncs."""
    if not path.exists():
        return {}, False
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        logging.getLogger("skill-sync").warning(
            "Ignoring invalid index %s: %s", path, error
        )
        return {}, False
    entries = value.get("entries", []) if isinstance(value, dict) else []
    if not isinstance(entries, list):
        return {}, False
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            result[entry["id"]] = entry
    skills = value.get("skills", []) if isinstance(value, dict) else []
    if isinstance(skills, list):
        for skill in skills:
            if isinstance(skill, dict) and isinstance(skill.get("id"), str):
                result[skill["id"]] = skill
    return result, bool(skills)


def relative_index_path(path: str | Path, base: Path) -> str:
    return Path(os.path.relpath(Path(path), base)).as_posix()


def path_creation_time(path: Path, fallback: str) -> str:
    try:
        created = dt.datetime.fromtimestamp(path.stat().st_ctime).astimezone()
    except OSError:
        return fallback
    return created.isoformat()


def write_root_index(
    args: argparse.Namespace,
    repositories: list[dict[str, Any]],
    external: list[dict[str, str]],
    results: list[RepositoryResult],
    generated_at: str,
    started_at: str,
) -> None:
    """Write a compact root index that points at the detailed state files."""
    index_path = args.index_path
    previous, had_previous_skills = load_index(index_path)
    result_by_key = {
        f"github:{result.name.casefold()}": result
        for result in results
        if result.type == "GitHub"
    }
    result_by_external_link = {
        result.name: result
        for result in results
        if result.type == "External"
    }
    base = Path(__file__).resolve().parent
    entries: list[dict[str, Any]] = []
    skills: list[dict[str, Any]] = []

    for repository in repositories:
        name = repository["repository"]
        entry_id = f"github:{name.casefold()}"
        result = result_by_key.get(entry_id)
        old = previous.get(entry_id, {})
        added_at = old.get("added_at") or path_creation_time(
            Path(repository["local_path"]), started_at
        )
        updated_at = old.get("updated_at") or added_at
        if result and result.status in {"Cloned", "Updated"}:
            updated_at = generated_at
        entries.append(
            {
                "id": entry_id,
                "type": "repository",
                "name": name,
                "path": relative_index_path(repository["local_path"], base),
                "sources": repository["sources"],
                "skill_count": len(repository.get("skills", [])),
                "status": result.status if result else old.get("status", "Pending"),
                "added_at": added_at,
                "updated_at": updated_at,
            }
        )
        for skill in repository.get("skills", []):
            source = str(skill.get("source", ""))
            skill_name = str(skill.get("name", ""))
            skill_link = str(skill.get("link", ""))
            skill_id = ":".join(
                (
                    entry_id,
                    source.casefold(),
                    skill_name.casefold(),
                    skill_link,
                )
            )
            old_skill = previous.get(skill_id, {})
            skill_added_at = old_skill.get("added_at")
            if not skill_added_at:
                skill_added_at = (
                    generated_at if had_previous_skills else added_at
                )
            skill_updated_at = old_skill.get("updated_at") or skill_added_at
            if result and result.status in {"Cloned", "Updated"}:
                skill_updated_at = generated_at
            skill_entry = {
                "id": skill_id,
                "name": skill_name,
                "repository": entry_id,
                "source": source,
                "path": relative_index_path(repository["local_path"], base),
                "status": result.status if result else old_skill.get("status", "Pending"),
                "added_at": skill_added_at,
                "updated_at": skill_updated_at,
            }
            for field in ("link", "category", "installs"):
                if field in skill:
                    skill_entry[field] = skill[field]
            skills.append(skill_entry)

    for item in external:
        name = item["name"]
        entry_id = f"external:{item['link']}"
        result = result_by_external_link.get(name)
        old = previous.get(entry_id, {})
        target = args.external_root / safe_path_segment(name)
        added_at = old.get("added_at") or path_creation_time(target, started_at)
        updated_at = old.get("updated_at") or added_at
        if result and result.status == "Downloaded":
            updated_at = generated_at
        entries.append(
            {
                "id": entry_id,
                "type": "external",
                "name": name,
                "link": item["link"],
                "path": relative_index_path(target, base),
                "source": item["source"],
                "category": item.get("category", ""),
                "status": result.status if result else old.get("status", "Pending"),
                "added_at": added_at,
                "updated_at": updated_at,
            }
        )
        skill_id = f"{entry_id}:skill"
        old_skill = previous.get(skill_id, {})
        skill_added_at = old_skill.get("added_at") or (
            generated_at if had_previous_skills else added_at
        )
        skill_updated_at = old_skill.get("updated_at") or skill_added_at
        if result and result.status == "Downloaded":
            skill_updated_at = generated_at
        skills.append(
            {
                "id": skill_id,
                "name": name,
                "repository": entry_id,
                "source": item["source"],
                "link": item["link"],
                "category": item.get("category", ""),
                "path": relative_index_path(target, base),
                "status": result.status if result else old_skill.get("status", "Pending"),
                "added_at": skill_added_at,
                "updated_at": skill_updated_at,
            }
        )

    entries.sort(key=lambda entry: (entry["type"], entry["name"].casefold()))
    skills.sort(key=lambda entry: (entry["name"].casefold(), entry["id"].casefold()))
    atomic_write_json(
        index_path,
        {
            "schema_version": INDEX_SCHEMA_VERSION,
            "generated_at": generated_at,
            "data": {
                "repositories": relative_index_path(
                    args.state_root / "repositories.json", base
                ),
                "external_links": relative_index_path(
                    args.state_root / "external-links.json", base
                ),
                "last_run": relative_index_path(args.state_root / "last-run.json", base),
                "manifest": relative_index_path(args.state_root / "skills.json", base),
                "official": relative_index_path(args.state_root / "official.json", base),
            },
            "skill_count": len(skills),
            "repository_count": len(repositories),
            "external_count": len(external),
            "entries": entries,
            "skills": skills,
        },
    )


def fetch_bytes(
    url: str,
    retries: int,
    timeout: int,
    logger: logging.Logger,
    proxy_url: str | None,
) -> tuple[bytes, str]:
    proxy_scheme = (
        urllib.parse.urlsplit(proxy_url).scheme.casefold() if proxy_url else ""
    )
    if proxy_scheme in {"socks5", "socks5h"}:
        return fetch_bytes_with_curl(url, retries, timeout, proxy_url)

    last_error: Exception | None = None
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler(
            {"http": proxy_url, "https": proxy_url} if proxy_url else {}
        )
    )
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
                },
            )
            with opener.open(request, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                return response.read(), content_type
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
            logger.warning(
                "Download failed for %s (attempt %d/%d): %s",
                url,
                attempt,
                retries,
                error,
            )
            if attempt < retries:
                time.sleep(min(10, attempt * 2))
    assert last_error is not None
    raise last_error


def fetch_bytes_with_curl(
    url: str, retries: int, timeout: int, proxy_url: str
) -> tuple[bytes, str]:
    curl = shutil.which("curl")
    if curl is None:
        raise RuntimeError("curl is required when a SOCKS proxy is configured")
    with tempfile.TemporaryDirectory(prefix="skill-source-") as temporary_directory:
        target = Path(temporary_directory) / "download"
        command = [
            curl,
            "--proxy",
            proxy_url,
            "--location",
            "--fail",
            "--silent",
            "--show-error",
            "--retry",
            str(max(0, retries - 1)),
            "--retry-all-errors",
            "--max-time",
            str(timeout),
            "--output",
            str(target),
            "--write-out",
            "%{content_type}",
            "--url",
            url,
        ]
        download = run_command(command, timeout=max(60, timeout * retries + 30))
        if download.returncode != 0:
            raise urllib.error.URLError(download.output or "curl download failed")
        return target.read_bytes(), download.output.strip()


def parse_official_page(document: bytes) -> dict[str, Any]:
    parser = ScriptCollector()
    parser.feed(document.decode("utf-8"))
    flight_parts: list[str] = []
    prefix = "self.__next_f.push("
    for script in parser.scripts:
        script = script.strip()
        if not script.startswith(prefix) or not script.endswith(")"):
            continue
        frame_text = script[len(prefix) : -1]
        try:
            frame = json.loads(frame_text)
        except json.JSONDecodeError:
            continue
        if len(frame) >= 2 and isinstance(frame[1], str):
            flight_parts.append(frame[1])

    flight = "".join(flight_parts)
    marker = '{"data":{"owners":'
    start = flight.find(marker)
    if start < 0:
        raise ValueError("skills.sh official owners payload was not found")
    payload, _ = json.JSONDecoder().raw_decode(flight[start:])
    owners = payload.get("data", {}).get("owners")
    if not isinstance(owners, list) or not owners:
        raise ValueError("skills.sh official owners payload is empty or invalid")
    return payload


def load_catalog_sources(
    args: argparse.Namespace, logger: logging.Logger
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_path = args.state_root / "skills.json"
    try:
        manifest_bytes, _ = fetch_bytes(
            args.manifest_url,
            args.retries,
            args.source_timeout,
            logger,
            args.proxy,
        )
        manifest = json.loads(manifest_bytes)
        if not isinstance(manifest.get("skills"), list):
            raise ValueError("manifest does not contain a skills list")
        atomic_write_bytes(manifest_path, manifest_bytes)
    except Exception as error:
        if not manifest_path.exists():
            raise
        logger.warning("Using cached skills.json after source failure: %s", error)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))

    official_html_path = args.state_root / "official.html"
    official_json_path = args.state_root / "official.json"
    try:
        official_bytes, _ = fetch_bytes(
            args.official_url,
            args.retries,
            args.source_timeout,
            logger,
            args.proxy,
        )
        official = parse_official_page(official_bytes)
        official["fetched_at"] = dt.datetime.now().astimezone().isoformat()
        atomic_write_bytes(official_html_path, official_bytes)
        atomic_write_json(official_json_path, official)
    except Exception as error:
        if not official_json_path.exists():
            raise
        logger.warning("Using cached official.json after source failure: %s", error)
        official = json.loads(official_json_path.read_text(encoding="utf-8"))
    return manifest, official


def github_repository_from_url(url: str) -> str | None:
    parsed = urllib.parse.urlsplit(url)
    if (parsed.hostname or "").casefold() not in {"github.com", "www.github.com"}:
        return None
    parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None
    repository = f"{parts[0]}/{parts[1]}"
    return normalize_repository_name(repository)


def normalize_repository_name(repository: str) -> str | None:
    if not REPOSITORY_PATTERN.fullmatch(repository):
        return None
    owner, name = repository.split("/", 1)
    while name.casefold().endswith(".git"):
        name = name[:-4]
    normalized = f"{owner}/{name}"
    return normalized if REPOSITORY_PATTERN.fullmatch(normalized) else None


def load_overrides(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("repository-overrides.json must contain an object")
    overrides: dict[str, dict[str, str]] = {}
    for repository, config in value.items():
        if not isinstance(config, dict):
            raise ValueError(f"override for {repository} must be an object")
        clone_url = str(config.get("cloneUrl", ""))
        parsed = urllib.parse.urlsplit(clone_url)
        if parsed.scheme != "https" or (parsed.hostname or "").casefold() != "github.com":
            raise ValueError(f"override for {repository} has an invalid GitHub URL")
        overrides[repository.casefold()] = {
            "clone_url": clone_url,
            "reason": str(config.get("reason", "")),
        }
    return overrides


def build_repository_index(
    manifest: dict[str, Any],
    official: dict[str, Any],
    repository_root: Path,
    overrides: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, int]]:
    repositories: dict[str, dict[str, Any]] = {}
    external: list[dict[str, str]] = []

    def get_repository(repository_name: str) -> dict[str, Any]:
        repository_name = normalize_repository_name(repository_name) or ""
        if not repository_name:
            raise ValueError(f"invalid GitHub repository name: {repository_name}")
        key = repository_name.casefold()
        if key not in repositories:
            owner, name = repository_name.split("/", 1)
            original_url = f"https://github.com/{owner}/{name}.git"
            override = overrides.get(key, {})
            repositories[key] = {
                "repository": repository_name,
                "original_clone_url": original_url,
                "clone_url": override.get("clone_url", original_url),
                "override_reason": override.get("reason") or None,
                "local_path": str(repository_root / owner / name),
                "sources": set(),
                "skills": [],
                "_skill_keys": set(),
            }
        return repositories[key]

    manifest_repository_keys: set[str] = set()
    for skill in manifest["skills"]:
        link = str(skill.get("link", ""))
        repository_name = github_repository_from_url(link)
        if repository_name is None:
            external.append(
                {
                    "name": str(skill.get("name", "external-item")),
                    "link": link,
                    "category": str(skill.get("category", "")),
                    "source": "anbeime/skill:data/skills.json",
                }
            )
            continue
        repository = get_repository(repository_name)
        repository["sources"].add("anbeime/skill:data/skills.json")
        manifest_repository_keys.add(repository["repository"].casefold())
        skill_record = {
            "name": str(skill.get("name", "")),
            "link": link,
            "category": str(skill.get("category", "")),
            "source": "anbeime/skill:data/skills.json",
        }
        skill_key = (skill_record["source"], skill_record["name"], link)
        if skill_key not in repository["_skill_keys"]:
            repository["_skill_keys"].add(skill_key)
            repository["skills"].append(skill_record)

    official_repository_keys: set[str] = set()
    owners = official.get("data", {}).get("owners", [])
    for owner_record in owners:
        for repo_record in owner_record.get("repos", []):
            repository_name = str(repo_record.get("repo", ""))
            repository = get_repository(repository_name)
            repository["sources"].add("skills.sh/official")
            official_repository_keys.add(repository["repository"].casefold())
            for skill in repo_record.get("skills", []):
                skill_record = {
                    "name": str(skill.get("name", "")),
                    "installs": int(skill.get("installs", 0)),
                    "source": "skills.sh/official",
                }
                skill_key = (skill_record["source"], skill_record["name"], "")
                if skill_key not in repository["_skill_keys"]:
                    repository["_skill_keys"].add(skill_key)
                    repository["skills"].append(skill_record)

    result: list[dict[str, Any]] = []
    for repository in repositories.values():
        repository.pop("_skill_keys")
        repository["sources"] = sorted(repository["sources"])
        repository["skills"].sort(
            key=lambda item: (item["source"].casefold(), item["name"].casefold())
        )
        result.append(repository)
    result.sort(key=lambda item: item["repository"].casefold())
    counts = {
        "manifest_repositories": len(manifest_repository_keys),
        "official_owners": len(owners),
        "official_repositories": len(official_repository_keys),
        "official_skill_records": sum(
            len(repo.get("skills", []))
            for owner in owners
            for repo in owner.get("repos", [])
        ),
        "combined_repositories": len(result),
        "overlap_repositories": len(manifest_repository_keys & official_repository_keys),
        "external_links": len(external),
    }
    return result, external, counts


def subprocess_flags() -> int:
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def acquire_sync_mutex() -> int | None:
    if os.name != "nt":
        return 1
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    handle = kernel32.CreateMutexW(None, True, SYNC_MUTEX_NAME)
    if not handle:
        raise ctypes.WinError()
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return None
    return int(handle)


def release_sync_mutex(handle: int) -> None:
    if os.name == "nt" and handle != 1:
        ctypes.windll.kernel32.ReleaseMutex(ctypes.c_void_p(handle))
        ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(handle))


def run_command(
    command: list[str],
    timeout: int,
    *,
    input_text: str | None = None,
    environment: dict[str, str] | None = None,
) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            input=input_text,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=environment,
            creationflags=subprocess_flags(),
            check=False,
        )
        return CommandResult(completed.returncode, completed.stdout.strip())
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return CommandResult(124, f"Command timed out after {timeout}s. {output}".strip())
    except OSError as error:
        return CommandResult(127, str(error))


def run_git(
    context: SyncContext,
    arguments: list[str],
    *,
    input_text: str | None = None,
    timeout: int | None = None,
) -> CommandResult:
    command = [context.git_executable]
    if os.name == "nt":
        command.extend(
            [
                "-c",
                "core.longpaths=true",
                "-c",
                "http.sslBackend=openssl",
            ]
        )
    if context.proxy_url:
        command.extend(["-c", f"http.proxy={context.proxy_url}"])
    command.extend(
        [
            "-c",
            "http.lowSpeedLimit=1024",
            "-c",
            "http.lowSpeedTime=60",
            "-c",
            "http.version=HTTP/1.1",
            *arguments,
        ]
    )
    environment = os.environ.copy()
    environment["GIT_TERMINAL_PROMPT"] = "0"
    return run_command(
        command,
        timeout or context.git_timeout,
        input_text=input_text,
        environment=environment,
    )


class GitOperationError(RuntimeError):
    pass


def discover_skill_directories(
    context: SyncContext, repository_path: Path
) -> tuple[list[str], int, int]:
    result = run_git(
        context,
        ["-C", str(repository_path), "ls-tree", "-r", "-z", "--name-only", "HEAD"],
    )
    if result.returncode != 0:
        raise GitOperationError(result.output or "git ls-tree failed")
    paths = [path for path in result.output.split("\0") if path]
    skill_paths = [
        PurePosixPath(path)
        for path in paths
        if PurePosixPath(path).name.casefold() == "skill.md"
    ]
    all_directories = {str(path.parent) for path in skill_paths}
    incompatible = sorted(
        directory
        for directory in all_directories
        if not windows_compatible_git_path(directory)
    )
    if incompatible:
        context.logger.warning(
            "Skipping %d Windows-incompatible skill path(s) in %s: %s",
            len(incompatible),
            repository_path,
            ", ".join(incompatible[:5]),
        )
    directories = sorted(
        all_directories - set(incompatible), key=lambda value: value.casefold()
    )
    return directories, len(skill_paths), len(incompatible)


def windows_compatible_git_path(path: str) -> bool:
    if os.name != "nt":
        return True
    invalid_characters = set('<>:"\\|?*')
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{number}" for number in range(1, 10)),
        *(f"LPT{number}" for number in range(1, 10)),
    }
    for part in PurePosixPath(path).parts:
        if any(character in invalid_characters for character in part):
            return False
        if part.endswith((" ", ".")):
            return False
        if part.split(".", 1)[0].upper() in reserved_names:
            return False
    return True


def is_sparse_checkout(context: SyncContext, repository_path: Path) -> bool:
    result = run_git(
        context,
        ["-C", str(repository_path), "config", "--bool", "core.sparseCheckout"],
        timeout=30,
    )
    return result.returncode == 0 and result.output.strip().casefold() == "true"


def is_partial_clone(context: SyncContext, repository_path: Path) -> bool:
    result = run_git(
        context,
        ["-C", str(repository_path), "config", "--bool", "remote.origin.promisor"],
        timeout=30,
    )
    return result.returncode == 0 and result.output.strip().casefold() == "true"


def configure_worktree(
    context: SyncContext,
    repository_path: Path,
    directories: list[str],
    skill_file_count: int,
    skipped_skill_file_count: int,
) -> str:
    sparse = is_sparse_checkout(context, repository_path)
    if skipped_skill_file_count:
        result = run_git(
            context,
            [
                "-C",
                str(repository_path),
                "config",
                "core.protectNTFS",
                "false",
            ],
            timeout=30,
        )
        if result.returncode != 0:
            raise GitOperationError(
                result.output or "could not configure Windows path compatibility"
            )

    if not skipped_skill_file_count and (skill_file_count == 0 or "." in directories):
        if sparse:
            result = run_git(
                context, ["-C", str(repository_path), "sparse-checkout", "disable"]
            )
        else:
            result = run_git(
                context, ["-C", str(repository_path), "checkout", "--quiet"]
            )
        if result.returncode != 0:
            raise GitOperationError(result.output or "full checkout failed")
        return "full"

    sparse_directories = [directory for directory in directories if directory != "."]
    if not sparse_directories:
        sparse_directories = ["__skill_sync_no_compatible_paths__"]

    result = run_git(
        context,
        ["-C", str(repository_path), "sparse-checkout", "init", "--cone"],
    )
    if result.returncode != 0:
        raise GitOperationError(result.output or "sparse-checkout init failed")
    result = run_git(
        context,
        ["-C", str(repository_path), "sparse-checkout", "set", "--stdin"],
        input_text="\n".join(sparse_directories) + "\n",
    )
    if result.returncode != 0:
        raise GitOperationError(result.output or "sparse-checkout set failed")
    return "sparse-partial" if skipped_skill_file_count else "sparse"


def remove_readonly(function: Any, path: str, error_info: Any) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def remove_clone_temporary(path: Path, repository_root: Path) -> None:
    if not path.exists():
        return
    root = repository_root.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(root) or not CLONE_TEMP_PATTERN.search(path.name):
        raise RuntimeError(f"refusing to remove unsafe clone path: {resolved}")
    shutil.rmtree(resolved, onerror=remove_readonly)


def clean_stale_clones(repository_root: Path, logger: logging.Logger) -> None:
    if not repository_root.exists():
        return
    for owner_path in repository_root.iterdir():
        if not owner_path.is_dir():
            continue
        for candidate in owner_path.iterdir():
            if candidate.is_dir() and CLONE_TEMP_PATTERN.search(candidate.name):
                logger.warning("Removing incomplete clone: %s", candidate)
                remove_clone_temporary(candidate, repository_root)


def retry_git(
    context: SyncContext, description: str, arguments: list[str]
) -> CommandResult:
    last_result = CommandResult(1, "command was not attempted")
    for attempt in range(1, context.retries + 1):
        last_result = run_git(context, arguments)
        if last_result.returncode == 0:
            return last_result
        if attempt < context.retries:
            context.logger.warning(
                "%s failed; retrying (%d/%d): %s",
                description,
                attempt + 1,
                context.retries,
                last_result.output,
            )
            time.sleep(min(10, attempt * 2))
    return last_result


def sync_existing_repository(
    context: SyncContext, repository: dict[str, Any], target: Path
) -> RepositoryResult:
    name = repository["repository"]
    head = run_git(
        context,
        ["-C", str(target), "rev-parse", "--verify", "HEAD"],
        timeout=30,
    )
    if head.returncode != 0:
        context.logger.info("Fetching empty repository %s", name)
        fetch = retry_git(
            context,
            f"Fetch for {name}",
            ["-C", str(target), "fetch", "--prune", "--quiet", "origin"],
        )
        if fetch.returncode != 0:
            return RepositoryResult(
                "GitHub", name, "Failed", fetch.output or "git fetch failed", str(target)
            )
        head = run_git(
            context,
            ["-C", str(target), "rev-parse", "--verify", "HEAD"],
            timeout=30,
        )
        if head.returncode != 0:
            return RepositoryResult(
                "GitHub", name, "Updated", None, str(target), "empty", 0, 0
            )

    if is_partial_clone(context, target) and not is_sparse_checkout(context, target):
        try:
            directories, skill_file_count, skipped_skill_file_count = (
                discover_skill_directories(context, target)
            )
            configure_worktree(
                context,
                target,
                directories,
                skill_file_count,
                skipped_skill_file_count,
            )
        except GitOperationError as error:
            return RepositoryResult(
                "GitHub",
                name,
                "Failed",
                f"Pre-pull sparse checkout repair failed: {error}",
                str(target),
            )

    context.logger.info("Pulling %s", name)
    pull = retry_git(
        context,
        f"Pull for {name}",
        ["-C", str(target), "pull", "--ff-only", "--prune", "--quiet"],
    )
    if pull.returncode != 0:
        return RepositoryResult(
            "GitHub", name, "Failed", pull.output or "git pull failed", str(target)
        )

    checkout_mode = "full"
    skill_file_count: int | None = None
    skipped_skill_file_count: int | None = None
    if is_sparse_checkout(context, target) or is_partial_clone(context, target):
        try:
            directories, skill_file_count, skipped_skill_file_count = (
                discover_skill_directories(context, target)
            )
            checkout_mode = configure_worktree(
                context,
                target,
                directories,
                skill_file_count,
                skipped_skill_file_count,
            )
        except GitOperationError as error:
            return RepositoryResult(
                "GitHub",
                name,
                "Failed",
                f"Pull succeeded but sparse checkout refresh failed: {error}",
                str(target),
            )
    return RepositoryResult(
        "GitHub",
        name,
        "Updated",
        None,
        str(target),
        checkout_mode,
        skill_file_count,
        skipped_skill_file_count,
    )


def prepare_new_clone(
    context: SyncContext, repository_path: Path
) -> tuple[str, int, int]:
    head = run_git(
        context,
        ["-C", str(repository_path), "rev-parse", "--verify", "HEAD"],
        timeout=30,
    )
    if head.returncode != 0:
        return "empty", 0, 0

    directories, skill_file_count, skipped_skill_file_count = (
        discover_skill_directories(context, repository_path)
    )
    try:
        checkout_mode = configure_worktree(
            context,
            repository_path,
            directories,
            skill_file_count,
            skipped_skill_file_count,
        )
    except GitOperationError as sparse_error:
        if skipped_skill_file_count:
            raise GitOperationError(
                "sparse checkout failed and a full checkout is unsafe on Windows: "
                f"{sparse_error}"
            ) from sparse_error
        context.logger.warning(
            "Sparse checkout failed for %s; trying a full checkout: %s",
            repository_path,
            sparse_error,
        )
        disable = run_git(
            context,
            ["-C", str(repository_path), "sparse-checkout", "disable"],
        )
        if disable.returncode != 0:
            checkout = run_git(
                context, ["-C", str(repository_path), "checkout", "--quiet"]
            )
            if checkout.returncode != 0:
                raise GitOperationError(checkout.output or str(sparse_error))
        checkout_mode = "full"

    reset = run_git(
        context,
        ["-C", str(repository_path), "reset", "--hard", "--quiet", "HEAD"],
    )
    if reset.returncode != 0:
        raise GitOperationError(reset.output or "new clone checkout initialization failed")
    return checkout_mode, skill_file_count, skipped_skill_file_count


def clone_repository(
    context: SyncContext, repository: dict[str, Any], target: Path
) -> RepositoryResult:
    name = repository["repository"]
    if repository.get("override_reason"):
        context.logger.warning(
            "Cloning %s from mirror %s: %s",
            name,
            repository["clone_url"],
            repository["override_reason"],
        )
    else:
        context.logger.info("Cloning %s", name)
    target.parent.mkdir(parents=True, exist_ok=True)
    last_output = ""

    for attempt in range(1, context.retries + 1):
        temporary = target.with_name(
            f"{target.name}.cloning-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        )
        try:
            clone = run_git(
                context,
                [
                    "clone",
                    "--quiet",
                    "--filter=blob:none",
                    "--depth=1",
                    "--single-branch",
                    "--no-checkout",
                    "--origin",
                    "origin",
                    "--",
                    repository["clone_url"],
                    str(temporary),
                ],
            )
            last_output = clone.output
            if clone.returncode == 0:
                checkout_mode, skill_file_count, skipped_skill_file_count = (
                    prepare_new_clone(context, temporary)
                )
                temporary.rename(target)
                return RepositoryResult(
                    "GitHub",
                    name,
                    "Cloned",
                    None,
                    str(target),
                    checkout_mode,
                    skill_file_count,
                    skipped_skill_file_count,
                )
        except (GitOperationError, OSError) as error:
            last_output = str(error)
        finally:
            if temporary.exists():
                remove_clone_temporary(temporary, context.repository_root)

        if attempt < context.retries:
            context.logger.warning(
                "Clone failed for %s; retrying (%d/%d): %s",
                name,
                attempt + 1,
                context.retries,
                last_output,
            )
            time.sleep(min(10, attempt * 2))

    if "repository not found" in last_output.casefold():
        context.logger.warning("%s is not publicly available", name)
        return RepositoryResult(
            "GitHub",
            name,
            "Unavailable",
            "The repository listed by the catalog is not publicly available.",
            str(target),
        )
    return RepositoryResult(
        "GitHub", name, "Failed", last_output or "git clone failed", str(target)
    )


def sync_repository(
    context: SyncContext, repository: dict[str, Any]
) -> RepositoryResult:
    target = Path(repository["local_path"])
    try:
        if target.exists():
            if not (target / ".git").is_dir():
                return RepositoryResult(
                    "GitHub",
                    repository["repository"],
                    "Failed",
                    "Target exists but is not a Git repository.",
                    str(target),
                )
            return sync_existing_repository(context, repository, target)
        return clone_repository(context, repository, target)
    except Exception as error:
        context.logger.exception("Unexpected error while syncing %s", repository["repository"])
        return RepositoryResult(
            "GitHub",
            repository["repository"],
            "Failed",
            str(error),
            str(target),
        )


def safe_path_segment(value: str) -> str:
    safe = re.sub(r"[^\w.-]+", "-", value, flags=re.UNICODE).strip("-. ")
    return (safe or "external-item")[:80].rstrip("-. ")


def sync_external_item(
    item: dict[str, str], args: argparse.Namespace, logger: logging.Logger
) -> RepositoryResult:
    target_directory = args.external_root / safe_path_segment(item["name"])
    temporary = target_directory / f"snapshot.tmp-{os.getpid()}"
    try:
        target_directory.mkdir(parents=True, exist_ok=True)
        curl = shutil.which("curl")
        if curl:
            curl_command = [
                curl,
                "--location",
                "--fail",
                "--silent",
                "--show-error",
                "--retry",
                str(max(0, args.retries - 1)),
                "--retry-all-errors",
                "--max-time",
                str(max(120, args.source_timeout)),
                "--output",
                str(temporary),
                "--write-out",
                "%{content_type}",
                "--url",
                item["link"],
            ]
            if args.proxy:
                curl_command[1:1] = ["--proxy", args.proxy]
            download = run_command(
                curl_command,
                timeout=max(180, args.source_timeout * args.retries),
            )
            if download.returncode != 0:
                raise RuntimeError(download.output or "curl download failed")
            content = temporary.read_bytes()
            content_type = download.output.strip()
        else:
            content, content_type = fetch_bytes(
                item["link"],
                args.retries,
                max(120, args.source_timeout),
                logger,
                args.proxy,
            )
        extension = ".html" if "html" in content_type.casefold() else ".bin"
        target = target_directory / f"snapshot{extension}"
        atomic_write_bytes(target, content)
        atomic_write_json(
            target_directory / "metadata.json",
            {
                **item,
                "downloaded_at": dt.datetime.now().astimezone().isoformat(),
                "content_type": content_type,
                "note": "This source is not a Git repository and is refreshed as a snapshot.",
            },
        )
        return RepositoryResult(
            "External", item["name"], "Downloaded", None, str(target)
        )
    except Exception as error:
        logger.error("External snapshot failed for %s: %s", item["name"], error)
        return RepositoryResult(
            "External",
            item["name"],
            "Failed",
            str(error),
            str(target_directory),
        )
    finally:
        temporary.unlink(missing_ok=True)


def save_run_summary(
    args: argparse.Namespace,
    started_at: dt.datetime,
    source_counts: dict[str, int],
    results: list[RepositoryResult],
    log_path: Path,
) -> tuple[list[RepositoryResult], list[RepositoryResult]]:
    results.sort(key=lambda result: (result.type.casefold(), result.name.casefold()))
    failed = [result for result in results if result.status == "Failed"]
    unavailable = [result for result in results if result.status == "Unavailable"]
    summary = {
        "started_at": started_at.isoformat(),
        "finished_at": dt.datetime.now().astimezone().isoformat(),
        "manifest_url": args.manifest_url,
        "official_url": args.official_url,
        "source_counts": source_counts,
        "failed_count": len(failed),
        "unavailable_count": len(unavailable),
        "results": [dataclasses.asdict(result) for result in results],
        "log_path": str(log_path),
    }
    atomic_write_json(args.state_root / "last-run.json", summary)
    return failed, unavailable


def main() -> int:
    args = parse_args()
    for directory in (
        args.repository_root,
        args.external_root,
        args.state_root,
        args.log_root,
        args.index_path.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    logger, log_path = setup_logging(args.log_root)
    started_at = dt.datetime.now().astimezone()
    mutex = acquire_sync_mutex()
    if mutex is None:
        logger.error("Another Python repository sync is already running")
        return 2
    atexit.register(release_sync_mutex, mutex)
    logger.info("Python skill repository sync started")

    try:
        git_executable = shutil.which("git")
        if git_executable is None:
            raise RuntimeError("git executable was not found")
        manifest, official = load_catalog_sources(args, logger)
        overrides = load_overrides(args.overrides)
        repositories, external, source_counts = build_repository_index(
            manifest, official, args.repository_root, overrides
        )
        atomic_write_json(args.state_root / "repositories.json", repositories)
        atomic_write_json(args.state_root / "external-links.json", external)
        logger.info(
            "Catalogs resolved to %d repositories: %d manifest, %d official, %d overlap",
            source_counts["combined_repositories"],
            source_counts["manifest_repositories"],
            source_counts["official_repositories"],
            source_counts["overlap_repositories"],
        )
        clean_stale_clones(args.repository_root, logger)
    except Exception as error:
        logger.exception("Catalog preparation failed: %s", error)
        return 1

    context = SyncContext(
        args.repository_root.resolve(),
        git_executable,
        args.retries,
        args.git_timeout,
        args.proxy,
        logger,
    )
    connectivity = retry_git(
        context,
        "GitHub connectivity check",
        ["ls-remote", "--exit-code", GITHUB_CONNECTIVITY_URL, "HEAD"],
    )
    if connectivity.returncode != 0:
        result = RepositoryResult(
            "System",
            "github.com",
            "Failed",
            connectivity.output or "GitHub Git connectivity check failed",
            "",
        )
        save_run_summary(args, started_at, source_counts, [result], log_path)
        write_root_index(
            args,
            repositories,
            external,
            [result],
            dt.datetime.now().astimezone().isoformat(),
            started_at.isoformat(),
        )
        logger.error("GitHub connectivity check failed; repository sync was skipped")
        return 1

    results: list[RepositoryResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {
            executor.submit(sync_repository, context, repository): repository
            for repository in repositories
        }
        for future in concurrent.futures.as_completed(future_map):
            results.append(future.result())

    for item in external:
        results.append(sync_external_item(item, args, logger))
    failed, unavailable = save_run_summary(
        args, started_at, source_counts, results, log_path
    )
    write_root_index(
        args,
        repositories,
        external,
        results,
        dt.datetime.now().astimezone().isoformat(),
        started_at.isoformat(),
    )

    try:
        projection = build_asuka_catalog(Path(__file__).resolve().parent)
        logger.info(
            "Asuka projection completed: %d packages, %d rejected, %d with omissions",
            projection["package_count"],
            projection["rejected_count"],
            projection["resource_omission_count"],
        )
    except Exception as error:
        logger.exception("Asuka projection failed; previous projection is retained: %s", error)
        return 1
    if failed:
        logger.error(
            "Sync finished with %d failed and %d unavailable item(s); "
            "Asuka projection used retained last-good mirrors",
            len(failed),
            len(unavailable),
        )
        return 1
    logger.info(
        "Sync completed: %d repositories, %d external link(s), %d unavailable",
        len(repositories),
        len(external),
        len(unavailable),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
