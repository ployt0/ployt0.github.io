import subprocess
from unittest.mock import patch, sentinel, Mock

import pytest

from common_git_utils import find_modified_files, git_add_updated


@patch("common_git_utils.subprocess.run", return_value=Mock(
    subprocess.CompletedProcess, returncode=0,
    stdout=b"M       file1.txt\nM       file2.html\nM       file3.html\n"))
def test_find_modified_files(mock_run):
    modified_html_files = find_modified_files(["html"])
    mock_run.assert_called_once_with("git diff --name-status --cached".split(), capture_output=True)
    assert modified_html_files == ["file2.html", "file3.html"]


@patch("common_git_utils.subprocess.run", return_value=Mock(
    subprocess.CompletedProcess, returncode=0,
    stdout=b"M       file1.txt\nD       file2.html\nM       file3.html\n"))
def test_find_modified_files_not_deleted(mock_run):
    modified_html_files = find_modified_files(["html"])
    mock_run.assert_called_once_with("git diff --name-status --cached".split(), capture_output=True)
    assert modified_html_files == ["file3.html"]


@patch("common_git_utils.subprocess.run", return_value=Mock(
    subprocess.CompletedProcess, returncode=0,
    stdout=b"M       file1.txt\nM       file2.txt\nM       file3.txt\n"))
def test_find_modified_files_all_text(mock_run):
    modified_html_files = find_modified_files(["html", "htm"])
    mock_run.assert_called_once_with("git diff --name-status --cached".split(), capture_output=True)
    assert modified_html_files == []


@patch("common_git_utils.subprocess.run", return_value=Mock(
    subprocess.CompletedProcess, returncode=1,
    stderr=b"This is a test", stdout=b"M       file1.html\n"))
def test_find_modified_files_git_error(mock_run):
    with pytest.raises(RuntimeError):
        find_modified_files(["html", "htm"])
    mock_run.assert_called_once_with("git diff --name-status --cached".split(), capture_output=True)


@patch("common_git_utils.subprocess.run", return_value=Mock(
    subprocess.CompletedProcess, returncode=0))
def test_git_add_updated(mock_run):
    git_add_updated(sentinel.changed_file)
    mock_run.assert_called_once_with(["git", "add", sentinel.changed_file], capture_output=True)


@patch("common_git_utils.subprocess.run", return_value=Mock(
    subprocess.CompletedProcess, returncode=1, stderr=b"This is a test"))
def test_git_add_updated_git_error(mock_run):
    with pytest.raises(RuntimeError):
        git_add_updated(sentinel.changed_file)
    mock_run.assert_called_once_with(["git", "add", sentinel.changed_file], capture_output=True)
