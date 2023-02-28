from dataclasses import dataclass, field

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
    show_result: bool = True
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


@dataclass
class build_result:
    student_name: str
    src_files_found: test_result = None  # type: ignore
    build: test_result = None     # type: ignore

    # if you don't do this, the attributes of the class will be shared between all instances
    def __post_init__(self):
        for attr in self.__dict__.keys():
            if self.__annotations__[attr] == test_result:
                setattr(self, attr, test_result())


@dataclass
class run_result:
    student_name: str
    input_bytes: bytes = None
    output: test_result = None     # type: ignore
    expected_output: list[str] = field(default_factory=list)     # type: ignore

    # if you don't do this, the attributes of the class will be shared between all instances
    def __post_init__(self):
        for attr in self.__dict__.keys():
            if self.__annotations__[attr] == test_result:
                setattr(self, attr, test_result())
