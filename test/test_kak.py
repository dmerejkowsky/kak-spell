from typing import Any
from kak_spell.kak import (
    convert_to_pos,
    convert_ranges,
    get_next_selection,
    get_previous_selection,
    goto_and_select,
)


def test_convert_to_pos_option() -> None:
    assert convert_to_pos("1.1") == (1, 1)


def test_convert_ranges_option() -> None:
    option = "1 1.21,1.30|Error 2.19,2.27|Error"
    assert convert_ranges(option) == [(1, 21, 30), (2, 19, 27)]


def test_get_next_selection_no_errors()


def test_get_next_selection_same_line_after_cursor() -> None:
    pos = (1, 1)
    ranges = [(1, 21, 30), (2, 19, 27)]
    assert get_next_selection(pos, ranges) == (1, 21, 30)


def test_get_next_selection_same_line_before_cursor() -> None:
    pos = (1, 15)
    ranges = [(1, 10, 14), (2, 19, 27)]
    assert get_next_selection(pos, ranges) == (2, 19, 27)


def test_get_next_selection_same_line_same_cursor() -> None:
    # Scenario: the cursor is at the end of the spell error -
    # we want to go to the next error, not stay where we are!
    pos = (1, 14)
    ranges = [(1, 10, 14), (2, 19, 27)]
    assert get_next_selection(pos, ranges) == (2, 19, 27)


def test_get_next_selection_end_of_buffer() -> None:
    pos = (3, 4)
    ranges = [(1, 10, 14), (2, 19, 27)]
    assert get_next_selection(pos, ranges) == (1, 10, 14)


def test_goto_and_select(capsys: Any) -> None:
    goto_and_select((2, 4, 9))
    capture = capsys.readouterr()

    assert not capture.err
    assert capture.out == "execute-keys 2g 3l 5L\n"


def test_get_previous_selection_same_line_after_cursor() -> None:
    pos = (1, 21)
    ranges = [(1, 12, 19), (2, 19, 27)]
    assert get_previous_selection(pos, ranges) == (1, 12, 19)


def test_get_previous_selection_same_line_before_cursor() -> None:
    pos = (1, 15)
    ranges = [(1, 3, 12), (2, 19, 27)]
    assert get_previous_selection(pos, ranges) == (1, 3, 12)


def test_get_previous_selection_same_line_same_cursor() -> None:
    # Scenario: the cursor is at the end of the spell error -
    # we want to go to the previous error, not stay where we are!
    pos = (2, 19)
    ranges = [(1, 10, 14), (2, 19, 27)]
    assert get_previous_selection(pos, ranges) == (1, 10, 14)