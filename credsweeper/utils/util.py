import logging
import math
import os
from typing import Dict, List, Tuple

from regex import regex
import whatthepatch

from credsweeper.common.constants import Chars, KeywordPattern, Separator


class Util:
    """
    Class that contains different useful methods
    """

    @classmethod
    def get_extension(cls, file_path: str) -> str:
        _, extension = os.path.splitext(file_path)
        return extension

    @classmethod
    def get_keyword_pattern(cls, keyword: str, separator: Separator = Separator.common) -> regex.Pattern:
        return regex.compile(KeywordPattern.key.format(keyword) + KeywordPattern.separator.format(separator) +
                             KeywordPattern.value,
                             flags=regex.IGNORECASE)

    @classmethod
    def get_regex_combine_or(cls, regex_strs: List[str]) -> str:
        result = "(?:"

        for elem in regex_strs:
            result += elem + "|"

        if result[-1] == "|":
            result = result[:-1]
        result += ")"

        return result

    @classmethod
    def is_entropy_validate(cls, data: str) -> bool:
        if cls.get_shannon_entropy(data, Chars.BASE64_CHARS) > 4.5 or \
           cls.get_shannon_entropy(data, Chars.HEX_CHARS) > 3 or \
           cls.get_shannon_entropy(data, Chars.BASE36_CHARS) > 3:
            return True
        return False

    @classmethod
    def get_shannon_entropy(cls, data: str, iterator: Chars) -> float:
        """
        Borrowed from http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html
        """
        if not data:
            return 0

        entropy = 0
        for x in iterator:
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += -p_x * math.log(p_x, 2)

        return entropy

    @classmethod
    def read_patch_file(cls, path: str) -> List[str]:
        with open(path, "r") as patch_file:
            diff_data = patch_file.readlines()
        return diff_data

    @classmethod
    def patch2files_diff(cls, raw_patch: List[str], change_type: str) -> Dict[str, List[Dict]]:
        """Generates files rows from diff with only added and deleted lines (e.g. marked + or - in diff)

        Args:
            raw_patch: string variable, Git diff output

        Return:
            return dict with {file paths:list of file row changes}, where
                elements of list of file row changes represented as:
                {
                    "old": line number before diff,
                    "new": line number after diff,
                    "line": line text,
                    "hunk": diff hunk number
                }
        """
        if not raw_patch:
            return {}

        # parse diff to patches
        patches = list(whatthepatch.parse_patch(raw_patch))
        added_files, deleted_files = {}, {}
        for patch in patches:
            if patch.changes is None:
                continue
            changes = []
            for change in patch.changes:
                changes.append(change._asdict())

            added_files[patch.header.new_path] = changes
            deleted_files[patch.header.old_path] = changes
        if change_type == "added":
            return added_files
        elif change_type == "deleted":
            return deleted_files
        else:
            logging.error(f"Change type should be one of: 'added', 'deleted'; but recieved {change_type}")
        return {}

    @classmethod
    def preprocess_file_diff(cls, changes: List[Dict], change_type: str) -> Tuple[List[int], List[str]]:
        """Generates files rows from diff with only added and deleted lines (e.g. marked + or - in diff)

        Args:
            out: string variable, Git diff output

        Return:
            Tuple of to lists: list of line numbers and list of line texts
        """
        add_rows, del_rows = [], []
        add_numbs, del_numbs = [], []
        if changes is None:
            return [], []

        # process diff to restore only added and deleted lines and their positions
        for change in changes:
            if change.get("old") is None:
                # indicates line was inserted
                add_rows.append(change.get("line"))
                add_numbs.append(change.get("new"))
            elif change.get("new") is None:
                # indicates line was removed
                del_rows.append(change.get("line"))
                del_numbs.append(change.get("old"))

        if change_type == "added":
            return add_numbs, add_rows
        elif change_type == "deleted":
            return del_numbs, del_rows
        else:
            logging.error(f"Change type should be one of: 'added', 'deleted'; but recieved {change_type}")
        return [], []
