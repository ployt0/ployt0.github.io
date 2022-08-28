"""
Useful to the pre-commit git hook to update the modification time of html files.

.git/hooks/pre-commit is where we should use it:

> #!/bin/sh
> ./script_to_using_modified_in_commit.py
"""
import os
import subprocess


def git_add_updated(changed_file: str) -> None:
    """
    Ensure modifications made by our script end up in the commit we are
    hooked in to.
    """
    re_add_completed = subprocess.run(["git", "add", changed_file], capture_output=True)
    if re_add_completed.returncode != 0:
        raise RuntimeError(re_add_completed.stderr.decode())


def find_modified_files(extensions: list[str]) -> list[str]:
    """
    :param extensions: only consider these file types.
    :return: list of modified files, as they appear to git (relative), that
        weren't deleted.
    """
    staged_files = subprocess.run("git diff --name-status --cached".split(), capture_output=True)
    if staged_files.returncode != 0:
        raise RuntimeError(staged_files.stderr.decode())
    extant_modded_files = []
    for line in staged_files.stdout.decode().strip().split("\n"):
        if not line.startswith("D") and \
                "." in line and \
                line.split(".")[-1] in extensions:
            extant_modded_files.append(line[1:].strip())
    return extant_modded_files


def find_mod_times(file_list: list[str]) -> list[tuple[str, float]]:
    modtime_pairs = []
    for f in file_list:
        latest_mtime = os.stat(f).st_mtime
        modtime_pairs.append((f, latest_mtime))
    return modtime_pairs

