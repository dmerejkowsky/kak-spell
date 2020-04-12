from typing import Any, List, Tuple
from . import log


def set_spell_errors(errors: Any, *, timestamp: int) -> None:
    cmd = f"set-option buffer spell_errors {timestamp}"
    n = 0
    for error in errors:
        line = error.line
        col = error.offset
        length = len(error.word)
        cmd += f" {line}.{col}+{length}|Error"
        n += 1
    log(cmd)
    print(cmd)
    if n:
        print("echo -markup {red}", n, "spelling error(s)")
    else:
        show_no_errors()


def menu_from_replacements(replacements: List[str]) -> None:
    menu = ""
    for entry in replacements:
        # Note: %{...} is kakoune way of grouping stuff that may - or not
        # contains quotes, which prevents us from using `%`, `.format()` or
        # f-strings :P
        # also note that we call 'write' and 'kak-spell' *in* the menu action, otherwise
        # if you call `write` *after* the menu command, the buffer is saved without the new
        # contents written !
        menu_entry = "%{ENTRY} %{execute-keys -itersel %{cENTRY<esc>be} <esc> :write <ret> :kak-spell <ret>}"
        menu_entry = menu_entry.replace("ENTRY", entry)
        menu += " " + menu_entry
    cmd = "menu " + menu
    print(cmd)


def show_no_errors():
    print("echo -markup {green} no spelling errors")


def goto_next(pos_option: str, ranges_option: str) -> None:
    cursor = convert_to_pos(pos_option)
    ranges = convert_ranges(ranges_option)
    if not ranges:
        show_no_errors()
        return
    next_selection = get_next_selection(cursor, ranges)
    goto_and_select(next_selection)


def goto_previous(pos_option: str, ranges_option: str) -> None:
    cursor = convert_to_pos(pos_option)
    ranges = convert_ranges(ranges_option)
    if not ranges:
        show_no_errors()
        return
    previous_selection = get_previous_selection(cursor, ranges)
    goto_and_select(previous_selection)


Pos = Tuple[int, int]
Range = Tuple[int, int, int]


# (line, col)
def convert_to_pos(pos_option: str) -> Pos:
    start, end = pos_option.split(".")
    return int(start), int(end)


# (line, col, length)
def convert_ranges(ranges_option: str) -> List[Range]:
    if ranges_option == "0":
        return []

    res = []
    ranges_list = ranges_option.split()[1:]
    for range_option in ranges_list:
        range_str = range_option.split("|")[0]  # strip face
        start, end = range_str.split(",")
        start_line, start_col = convert_to_pos(start)
        end_line, end_col = convert_to_pos(end)
        res.append((start_line, start_col, end_col))
    return res


def goto_and_select(range: Range) -> None:
    line, col, end = range
    length = end - col
    cmd = f"execute-keys {line}g {col-1}l {length}L"
    print(cmd)


def get_next_selection(cursor: Pos, ranges: List[Range]) -> Range:
    cursor_line, cursor_col = cursor
    for r in ranges:
        start_line, start_col, end_col = r
        if start_line < cursor_line:
            continue
        if start_line == cursor_line and end_col <= cursor_col:
            continue
        return r
    # if we reach there, return the first error (auto-wrap)
    return ranges[0]


def get_previous_selection(cursor: Pos, ranges: List[Range]) -> Range:
    cursor_line, cursor_col = cursor
    for r in reversed(ranges):
        start_line, start_col, end_col = r
        if start_line > cursor_line:
            continue
        if start_line == cursor_line and end_col > cursor_col:
            continue
        return r
    # if we reach there, return the last error (auto-wrap)
    return ranges[-1]