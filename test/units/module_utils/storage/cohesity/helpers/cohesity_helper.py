import re


class reg_verify:
    """Assert that a given string meets some expectations."""

    def __init__(self, pattern, flags=0):
        self._regex = re.compile(pattern, flags)

    def __check__(self, actual):
        return bool(self._regex.match(actual))

    def __repr__(self):
        return self._regex.pattern
