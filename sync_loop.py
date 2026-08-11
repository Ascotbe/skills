from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import logging
import logging.handlers
import os
import subprocess
import sys
import time
from pathlib import Path


ERROR_ALREADY_EXISTS = 183


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the skill sync once per day.")
    parser.add_argument("--daily-at", default="03:00")
    parser.add_argument("--poll-seconds", type=int, default=60)
    args = parser.parse_args()
    try:
        dt.time.fromisoformat(args.daily_at)
    except ValueError as error:
        parser.error(str(error))
    if not 30 <= args.poll_seconds <= 3600:
        parser.error("--poll-seconds must be between 30 and 3600")
    return args


def setup_logging(base: Path) -> logging.Logger:
    log_root = base / "logs"
    log_root.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("skill-sync-loop")
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        log_root / "loop.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
    )
    logger.addHandler(handler)
    return logger


def acquire_mutex() -> int | None:
    if os.name != "nt":
        return 1
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    handle = kernel32.CreateMutexW(None, True, "Local\\SkillRepositoriesDailySync")
    if not handle:
        raise ctypes.WinError()
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return None
    return int(handle)


def release_mutex(handle: int) -> None:
    if os.name == "nt" and handle != 1:
        ctypes.windll.kernel32.ReleaseMutex(ctypes.c_void_p(handle))
        ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(handle))


def load_last_run(path: Path) -> dict[str, object] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def python_console_executable() -> Path:
    executable = Path(sys.executable)
    if executable.name.casefold() == "pythonw.exe":
        candidate = executable.with_name("python.exe")
        if candidate.exists():
            return candidate
    return executable


def run_sync(base: Path, logger: logging.Logger) -> int:
    command = [str(python_console_executable()), str(base / "sync_skills.py")]
    logger.info("Starting scheduled sync")
    completed = subprocess.run(
        command,
        cwd=base,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        check=False,
    )
    logger.info("Scheduled sync exited with code %d", completed.returncode)
    return completed.returncode


def main() -> int:
    args = parse_args()
    base = Path(__file__).resolve().parent
    logger = setup_logging(base)
    mutex = acquire_mutex()
    if mutex is None:
        return 0

    state_root = base / "state"
    state_root.mkdir(parents=True, exist_ok=True)
    pid_path = state_root / "sync-loop.pid"
    pid_path.write_text(str(os.getpid()), encoding="ascii")
    scheduled_time = dt.time.fromisoformat(args.daily_at)
    attempt_date: dt.date | None = None
    attempts = 0
    last_attempt_at: dt.datetime | None = None

    try:
        logger.info("Python sync loop started; daily time is %s", args.daily_at)
        while True:
            now = dt.datetime.now().astimezone()
            if attempt_date != now.date():
                attempt_date = now.date()
                attempts = 0
                last_attempt_at = None

            scheduled_today = dt.datetime.combine(
                now.date(), scheduled_time, tzinfo=now.tzinfo
            )
            should_run = now >= scheduled_today and attempts < 3
            last_run = load_last_run(state_root / "last-run.json")
            if should_run and last_run:
                try:
                    finished = dt.datetime.fromisoformat(str(last_run["finished_at"]))
                    failed_count = int(last_run.get("failed_count", 0))
                    if finished >= scheduled_today and failed_count == 0:
                        should_run = False
                    elif failed_count > 0 and finished + dt.timedelta(minutes=15) > now:
                        should_run = False
                except (KeyError, TypeError, ValueError):
                    pass
            if (
                should_run
                and last_attempt_at is not None
                and last_attempt_at + dt.timedelta(minutes=15) > now
            ):
                should_run = False

            if should_run:
                attempts += 1
                last_attempt_at = now
                run_sync(base, logger)
            time.sleep(args.poll_seconds)
    finally:
        try:
            if pid_path.read_text(encoding="ascii").strip() == str(os.getpid()):
                pid_path.unlink(missing_ok=True)
        except OSError:
            pass
        release_mutex(mutex)


if __name__ == "__main__":
    raise SystemExit(main())
