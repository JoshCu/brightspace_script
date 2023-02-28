import sys
import pathlib

from dataclasses import dataclass

from ....common_datamodels import test_result


@dataclass
class part1:
    student_name: str
    rsa_file_found: test_result = None     # type: ignore
    rsa_file_compiles: test_result = None  # type: ignore
    rsa_file_runs: test_result = None      # type: ignore
    keys_file_found: test_result = None    # type: ignore
    grading_builds: test_result = None     # type: ignore
    grading_runs: test_result = None       # type: ignore

    # if you don't do this, the attributes of the class will be shared between all instances
    def __post_init__(self):
        for attr in self.__dict__.keys():
            if self.__annotations__[attr] == test_result:
                setattr(self, attr, test_result())

    # allows you to access the attributes of the class using index like syntax
    def __getitem__(self, items):
        return getattr(self, items)


@dataclass
class part2:
    student_name: str
    message_file_found: test_result = None     # type: ignore
    message_file_compiles: test_result = None  # type: ignore
    one_line_signed: test_result = None        # type: ignore
    one_line_verified: test_result = None      # type: ignore
    one_line_modified: test_result = None      # type: ignore
    two_lines_signed: test_result = None       # type: ignore
    two_lines_verified: test_result = None     # type: ignore
    two_lines_modified: test_result = None     # type: ignore
    bible_part1_signed: test_result = None     # type: ignore
    bible_part1_verified: test_result = None   # type: ignore
    bible_part1_modified: test_result = None   # type: ignore

    # if you don't do this, the attributes of the class will be shared between all instances
    def __post_init__(self):
        for attr in self.__dict__.keys():
            if self.__annotations__[attr] == test_result:
                setattr(self, attr, test_result())

    # allows you to access the attributes of the class using index like syntax
    def __getitem__(self, items):
        return getattr(self, items)
