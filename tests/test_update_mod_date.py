import datetime
from unittest.mock import patch, mock_open, sentinel, Mock, call

import pytest

from update_mod_date import main, replace_footer, cmp_and_overwrite_mtime, \
    check_changes, validate_html

SAMPLE_HTML = '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Sentinel.Site</title>
</head>
<body>
<header>
Branding
</header>
<nav>
<h3>Posts:</h3>
<ul>
<li>Foo</li>
<li>Bar</li>
</ul>
</nav>
<footer>
<small>published: 18/Jan/2019 modified: 19/Jan/2019</small>
</footer>
</body>
</html>
'''

EXPECTED_HTML = '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Sentinel.Site</title>
</head>
<body>
<header>
Branding
</header>
<nav>
<h3>Posts:</h3>
<ul>
<li>Foo</li>
<li>Bar</li>
</ul>
</nav>
<footer>
<hr>
<small>updated 31/Dec/2021</small>
</footer>
</body>
</html>
'''

MINIMAL_HTML = '''\
<body>call me .html</body>
'''

EXPECTED_MINIMAL_HTML = '''\
<body>call me .html<footer>
<hr>
<small>updated 31/Dec/2021</small>
</footer>
</body>
'''

BAD_HTML = '''\
<em>Glorified text</em>
'''


@patch("update_mod_date.git_add_updated")
@patch("update_mod_date.replace_footer", return_value="SENTINEL HTML")
@patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_HTML)
def test_cmp_and_overwrite_mtime(mocked_open, mock_replace_footer, mock_git_add_updated):
    cmp_and_overwrite_mtime(sentinel.file_name, '31/Dec/2021', False)
    mocked_open.assert_has_calls([
        call(sentinel.file_name, encoding='utf8'),
        call(sentinel.file_name, 'w', encoding='utf8')
    ], any_order=True)
    mock_replace_footer.assert_called_once_with(SAMPLE_HTML, '31/Dec/2021', sentinel.file_name)
    mocked_open.return_value.write.assert_called_once_with('SENTINEL HTML')
    mock_git_add_updated.assert_called_once_with(sentinel.file_name)


@patch("update_mod_date.git_add_updated")
@patch("update_mod_date.replace_footer", return_value="SENTINEL HTML")
@patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_HTML)
def test_cmp_and_overwrite_mtime_with_bkup(mocked_open, mock_replace_footer, mock_git_add_updated):
    cmp_and_overwrite_mtime("original_file_name", '31/Dec/2021', True)
    mocked_open.assert_has_calls([
        call("original_file_name", encoding='utf8'),
        call("original_file_name", 'w', encoding='utf8'),
        call("original_file_name" + ".bkup", 'w', encoding='utf8')
    ], any_order=True)
    mock_replace_footer.assert_called_once_with(SAMPLE_HTML, '31/Dec/2021', "original_file_name")
    mocked_open.return_value.write.assert_has_calls([
        call('SENTINEL HTML'),
        call(SAMPLE_HTML),
    ])
    mock_git_add_updated.assert_called_once_with("original_file_name")


@patch("update_mod_date.git_add_updated")
@patch("update_mod_date.replace_footer", return_value=EXPECTED_HTML)
@patch("builtins.open", new_callable=mock_open, read_data=EXPECTED_HTML)
def test_cmp_and_overwrite_mtime_redundant(mocked_open, mock_replace_footer, mock_git_add_updated):
    cmp_and_overwrite_mtime(sentinel.file_name, '31/Dec/2021', True)
    mocked_open.assert_called_once_with(sentinel.file_name, encoding='utf8')
    mock_replace_footer.assert_called_once_with(EXPECTED_HTML, '31/Dec/2021', sentinel.file_name)
    mocked_open.return_value.write.assert_not_called()
    mock_git_add_updated.assert_not_called()


@patch("update_mod_date.git_add_updated")
@patch("update_mod_date.replace_footer", side_effect=RuntimeError("Test only"))
@patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_HTML)
def test_validate_html(mocked_open, mock_replace_footer, mock_git_add_updated):
    with pytest.raises(RuntimeError):
        validate_html(sentinel.file_name)
    mocked_open.assert_called_once_with(sentinel.file_name, encoding='utf8')
    mock_replace_footer.assert_called_once_with(SAMPLE_HTML, 'unused', sentinel.file_name)
    mocked_open.return_value.write.assert_not_called()
    mock_git_add_updated.assert_not_called()


def test_replace_footer():
    updated_html = replace_footer(SAMPLE_HTML, "31/Dec/2021", "good.html")
    assert updated_html == EXPECTED_HTML


def test_replace_footer_redundant():
    updated_html = replace_footer(EXPECTED_HTML, "31/Dec/2021", "good.html")
    assert updated_html == EXPECTED_HTML


def test_replace_footer_minimal_html():
    updated_html = replace_footer(MINIMAL_HTML, "31/Dec/2021", "minimal.html")
    assert updated_html == EXPECTED_MINIMAL_HTML


def test_replace_footer_bad_html():
    with pytest.raises(RuntimeError):
        replace_footer(BAD_HTML, "31/Dec/2021", "bad.html")


@patch("update_mod_date.cmp_and_overwrite_mtime")
@patch("update_mod_date.find_modified_files", return_value=["sentinel1.txt", "sentinel2.txt"])
@patch("update_mod_date.datetime", spec=datetime)
def test_main(mock_datetime, mock_find_modified_files, mock_cmp_and_overwrite_mtime):
    mock_datetime.utcnow = Mock(
        side_effect=[datetime.datetime(2021, 12, 31, 12, 30, 00)] * 2)
    main()
    mock_find_modified_files.assert_called_once_with(["html", "htm"])
    mock_cmp_and_overwrite_mtime.assert_has_calls([
        call("sentinel1.txt", '31/Dec/2021', False),
        call("sentinel2.txt", '31/Dec/2021', False)
    ])


@patch("update_mod_date.validate_html")
@patch("update_mod_date.find_modified_files", return_value=["sentinel1.txt", "sentinel2.txt"])
def test_check_changes(mock_find_modified_files, mock_validate_html):
    check_changes()
    mock_find_modified_files.assert_called_once_with(["html", "htm"])
    mock_validate_html.assert_has_calls([
        call("sentinel1.txt"),
        call("sentinel2.txt")
    ])
