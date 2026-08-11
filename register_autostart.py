from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import winreg
from pathlib import Path


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "SkillRepositories-DailySync"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Register the Python skill sync loop for the current user."
    )
    parser.add_argument("--daily-at", default="03:00")
    parser.add_argument("--no-start", action="store_true")
    return parser.parse_args()


def find_pythonw() -> Path:
    executable = Path(sys.executable).resolve()
    candidate = executable.with_name("pythonw.exe")
    if candidate.exists():
        return candidate
    return executable


def process_exists(process_id: int) -> bool:
    if os.name != "nt":
        return True
    import ctypes

    process = ctypes.windll.kernel32.OpenProcess(0x1000, False, process_id)
    if not process:
        return False
    ctypes.windll.kernel32.CloseHandle(process)
    return True


def main() -> int:
    args = parse_args()
    base = Path(__file__).resolve().parent
    loop_script = base / "sync_loop.py"
    pythonw = find_pythonw()
    command = f'"{pythonw}" "{loop_script}" --daily-at "{args.daily_at}"'

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, command)

    process_id: int | None = None
    if not args.no_start:
        subprocess.Popen(
            [str(pythonw), str(loop_script), "--daily-at", args.daily_at],
            cwd=base,
            creationflags=(
                subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                if os.name == "nt"
                else 0
            ),
            close_fds=True,
        )
        pid_path = base / "state" / "sync-loop.pid"
        for _ in range(50):
            try:
                candidate = int(pid_path.read_text(encoding="ascii").strip())
                if process_exists(candidate):
                    process_id = candidate
                    break
            except (OSError, ValueError):
                pass
            time.sleep(0.1)

    print(
        json.dumps(
            {
                "mode": "current-user Python startup loop",
                "registry_value": VALUE_NAME,
                "schedule": f"daily at {args.daily_at} local time",
                "command": command,
                "process_id": process_id,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
