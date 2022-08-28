#!/usr/bin/env python3

"""
Used by the pre-commit git hook to update the modification time of html files.
Still inferior to a dedicated CMS because we don't distinguish modification of
structure, formatting, and style etc from content.

Copying this very file .git/hooks/pre-commit *may* work. Mine is:

> #!/bin/sh
> ./update_mod_date.py

To verify, commit from the shell and if no html content was updated you should
see something like:

```
Checking times of: []
[master ff457b1] Library providing actual mtime to replace commit date.
 2 files changed, 21 insertions(+), 3 deletions(-)
```
"""

from datetime import datetime

from common_git_utils import git_add_updated, find_modified_files

DATE_TIME_FMT = "%y%m%d %H:%M:%S"


def validate_html(file_to_check: str):
    with open(file_to_check, encoding="utf8") as f:
        replace_footer(f.read(), "unused", file_to_check)


def cmp_and_overwrite_mtime(changed_file: str, mod_time_stamp: str, save_original: bool) -> None:
    """
    :param changed_file: single file to update with mod_time_stamp.
    :param mod_time_stamp: to place in footer of file.
    :param save_original: makes a backup (appending ".bkup") of any file being modified.
        I'd really rather not have this option; it makes more files to manage,
        but it helps whilst this script earns trust.
    """
    with open(changed_file, encoding="utf8") as f:
        html_contents = f.read()
    updated_html = replace_footer(html_contents, mod_time_stamp, changed_file)
    if updated_html == html_contents:
        # No sense in changing the timestamp or re-adding if nothing changed.
        return
    print("Adding today's date (in footer) to an updated {}".format(changed_file))
    with open(changed_file, "w", encoding="utf8") as f:
        f.write(updated_html)
    if save_original:
        print("Saving original as {}.bkup".format(changed_file))
        with open(changed_file + ".bkup", "w", encoding="utf8") as f:
            f.write(html_contents)
    git_add_updated(changed_file)


def replace_footer(html_text: str, mod_time_stamp: str, source_name: str) -> str:
    if "<footer>" not in html_text and "</body>" not in html_text:
        raise RuntimeError("Malformed HTML. {} requires at least a closing </body> tag.".format(source_name))
    if "<footer>" not in html_text:
        html_text = html_text.replace("</body>", "<footer></footer>\n</body>")
    pieces1 = html_text.split("<footer>")
    aft = pieces1[1]
    pieces2 = aft.split("</footer>")
    if "updated {}".format(mod_time_stamp) in pieces2[0]:
        return html_text
    footer = "<footer>\n<hr>\n<small>updated {}</small>\n</footer>".format(mod_time_stamp)
    return pieces1[0] + footer + pieces2[1]


def main():
    mod_time_stamp = datetime.utcnow().strftime("%d/%b/%Y")
    changed_files = find_modified_files(["html", "htm"])
    print("Checking times of: {}".format(changed_files))
    for changed_file in changed_files:
        cmp_and_overwrite_mtime(changed_file, mod_time_stamp, False)


def check_changes():
    changed_files = find_modified_files(["html", "htm"])
    for file_to_check in changed_files:
        validate_html(file_to_check)

#     <meta name="DC.Date" content="en" />
# Consider creation date, maybe


if __name__ == "__main__":
    # Test all the files before proceeding to update the modification time.
    check_changes()
    main()
