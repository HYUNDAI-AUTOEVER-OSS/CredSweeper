from typing import Dict, List, Optional

from credsweeper.file_handler.analysis_target import AnalysisTarget
from credsweeper.file_handler.content_provider import ContentProvider


class TextContentProvider(ContentProvider):
    """Provide access to analysis targets for full-text file scanning

    Attributes:
        self.file_path: string, path to file

    """
    def __init__(self,
                 file_path: str,
                 change_type: Optional[str] = None,
                 diff: Optional[List[Dict]] = None) -> None:
        self.file_path = file_path

    def get_analysis_target(self) -> List[AnalysisTarget]:
        """Load and preprocess file content to scan

        Return:
            list of analysis targets based on every row in file
        """
        with open(self.file_path) as f:
            all_lines = f.read().split("\n")
        return [AnalysisTarget(line, i + 1, all_lines, self.file_path) for i, line in enumerate(all_lines)]
