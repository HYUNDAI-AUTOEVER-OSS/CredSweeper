from regex import regex

from credsweeper.credentials import LineData
from credsweeper.filters import Filter

DEFAULT_PATTERN_LEN = 4


class ValuePatternCheck(Filter):
    """
    Similar to linguistic sequences of characters, random strings shouldn't contain math sequences of
    characters. PatternCheck checks the occurrence in "line_data.value" of three types of sequence:
        - N or more identical characters in sequence, example: "AAAA", "1111" ...
        - N or more increasing characters sequentially, example: "abcd", "1234" ...
        - N or more decreasing characters sequentially, example: "dcba", "4321" ...
    Default N is 4
    """
    def __init__(self, pattern_len: int = DEFAULT_PATTERN_LEN):
        """Create ValuePatternCheck with a specific pattern_len to check

        Args:
            pattern_len: pattern len to use during check. DEFAULT_PATTERN_LEN by default
        """
        self.pattern_len = pattern_len

    def equal_pattern_check(self, line_data_value: str) -> bool:
        """Check if candidate value contain 4 and more same chars or
        numbers sequences

        Args:
            line_data_value: string variable, credential candidate value

        Return:
            boolean variable. True if contain and False if not
        """
        pattern_string = "(.)\\1{" + str(self.pattern_len - 1) + ",}"
        if regex.findall(pattern_string, line_data_value):
            return True
        return False

    def ascending_pattern_check(self, line_data_value: str) -> bool:
        """Check if candidate value contain 4 and more ascending chars or
        numbers sequences

        Arg:
            line_data_value: string variable, credential candidate value

        Return:
            boolean variable. True if contain and False if not
        """
        if not line_data_value:
            return False

        count = 1
        for key in range(len(line_data_value) - 1):
            if ord(line_data_value[key + 1]) - ord(line_data_value[key]) == 1:
                count += 1
            else:
                count = 1
                continue
            if count == self.pattern_len:
                return True
        return False

    def descending_pattern_check(self, line_data_value: str) -> bool:
        """Check if candidate value contain 4 and more descending chars or
        numbers sequences

        Arg:
            line_data_value: string variable, credential candidate value

        Return:
            boolean variable. True if contain and False if not
        """
        if not line_data_value:
            return False

        count = 1
        for key in range(len(line_data_value) - 1):
            if ord(line_data_value[key]) - ord(line_data_value[key + 1]) == 1:
                count += 1
            else:
                count = 1
                continue
            if count == self.pattern_len:
                return True
        return False

    def run(self, line_data: LineData) -> bool:
        """Run filter checks on received credential candidate data 'line_data'

        Arg:
            line_data: LineData object, credential candidate data

        Return:
            boolean variable. True, if need to filter candidate and False if left
        """
        if not line_data.value or len(line_data.value) < self.pattern_len:
            return True

        if self.equal_pattern_check(line_data.value):
            return True

        if self.ascending_pattern_check(line_data.value):
            return True

        if self.descending_pattern_check(line_data.value):
            return True

        return False
