from dataclasses import dataclass
from enum import Enum
from typing import Callable


@dataclass
class argument():
    function = Callable
    args = list


class exit_code(Enum):
    SUCCESS = 0
    ERROR = 1
    NOT_ATTEMPTED = -1


@dataclass
class test_result:
    # if exit code isn't valid, then set it to 1
    result: str = ""
    _exit_code: int = exit_code.NOT_ATTEMPTED.value

    @property
    def exit_code(self):
        return self._exit_code

    @exit_code.setter
    def exit_code(self, value):
        if not any(value == code.value for code in exit_code):
            self._exit_code = 1
        else:
            self._exit_code = value
