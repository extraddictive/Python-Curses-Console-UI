import curses.ascii
import sys
import os
import curses
import time

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _curses import _CursesWindow
    CursesWindowType = _CursesWindow
else:
    from typing import Any
    CursesWindowType = Any

if os.name == "nt":
    KEY_BACKSPACE = 8
else:
    KEY_BACKSPACE = curses.KEY_BACKSPACE



el = "\r"
nl = "\n"

def isIpPortChar(c: int):
    return curses.ascii.isdigit(c) or c == ord(".") or c == ord(":")

class checkBox():
    def __init__(self,
                 x: int,
                 y: int,
                 window: CursesWindowType,
                 label: str = "",
                 checkedColorPair: int = None,
                 uncheckedColorPair: int = None) -> None:
        self.x = x
        self.y = y
        self.len = len(label) + 3
        self.win = window
        self.label = label
        self.checkedColorPair = checkedColorPair
        self.uncheckedColorPair = uncheckedColorPair
        self._checked = False

    def _drawUnchecked(self):

            drawStr = self.label + "[ ]"
            if len(drawStr) == 0 and self.label:
                drawStr = self.label

            if len(drawStr) < self.len:
                drawStr += "_" * (self.len - len(drawStr))

            if self.uncheckedColorPair:
                self.win.addstr(self.y, self.x, drawStr, curses.color_pair(self.uncheckedColorPair))
            else:
                self.win.addstr(self.y, self.x, drawStr)

    def _drawChecked(self):

            drawStr = self.label + "[X]"
            if len(drawStr) < self.len:
                drawStr += "<"
                drawStr += "_" * (self.len - len(drawStr))

            if self.checkedColorPair:
                self.win.addstr(self.y, self.x, drawStr, curses.color_pair(self.checkedColorPair))
            else:
                self.win.addstr(self.y, self.x, drawStr)

    def draw(self):
        if self._checked:
            self._drawChecked()
        else:
            self._drawUnchecked()

    def check(self):
        self._checked = True

    def uncheck(self):
        self._checked = False

    def click(self,
              x: int,
              y: int):
        if y == self.y and self.x <= x <= self.x + self.len:
            if self._checked:
                self.uncheck()
                return
            self.check()

class stringField():
    def __init__(self,
                 x: int,
                 y: int,
                 length: int,
                 window: CursesWindowType,
                 default: str = None,
                 selColorPair: int = None,
                 uslColorPair: int = None,
                 inputFilter: callable = isIpPortChar) -> None:
        self.x = x
        self.y = y
        self.len = length
        self.win = window
        self.default = default
        self.selColorPair = selColorPair
        self.uslColorPair = uslColorPair
        self.string = ""
        self.filter = inputFilter
        self._selected = False

    def _drawUnselected(self):

            drawStr = self.string
            if len(drawStr) == 0 and self.default:
                drawStr = self.default

            if len(drawStr) < self.len:
                drawStr += "_" * (self.len - len(drawStr))

            if self.uslColorPair:
                self.win.addstr(self.y, self.x, drawStr, curses.color_pair(self.uslColorPair))
            else:
                self.win.addstr(self.y, self.x, drawStr)

    def _drawSelected(self):

            drawStr = self.string
            if len(drawStr) < self.len:
                drawStr += "<"
                drawStr += "_" * (self.len - len(drawStr))

            if self.selColorPair:
                self.win.addstr(self.y, self.x, drawStr, curses.color_pair(self.selColorPair))
            else:
                self.win.addstr(self.y, self.x, drawStr)

    def draw(self):
        if self._selected:
            self._drawSelected()
        else:
            self._drawUnselected()

    def select(self):
        self._selected = True

    def unselect(self):
        self._selected = False

    def writech(self,
                c: int):
        if self._selected:
            if len(self.string) < self.len and self.filter(c):
                self.string += chr(c)

            if c == KEY_BACKSPACE and len(self.string) > 0:
                self.string = self.string[:-1]

            if c == 10:
                self.unselect()

    def click(self,
              x: int,
              y: int):
        if y == self.y and self.x <= x <= self.x + self.len:
            self.select()
            return
        self.unselect()

def console(screen: CursesWindowType):
    curses.start_color()
    curses.init_pair( 1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair( 3, curses.COLOR_YELLOW, curses.COLOR_WHITE)

    wInfo = curses.newwin(6, curses.COLS, 0, 0)
    sInfo = stringField(1, 0, 20, wInfo, "ip:port", 1)
    c_sus = checkBox(1, 3, wInfo, "Impostor", 1)
    #curses.noecho()
    curses.curs_set(0)
    curses.cbreak()
    screen.keypad(1)
    curses.mousemask(1)
    border = ord("|")
    mouse = ""
    while True:
        c = screen.getch()
        if c == curses.KEY_RESIZE:
            rows, cols = screen.getmaxyx()
            wInfo.resize(6, cols)

        if c == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            mouse = f"x:{mx} y:{my}\r"
            sInfo.click(mx, my)
            c_sus.click(mx, my)

        wInfo.clear()
        wInfo.border(border, border,
                ord(" "), ord("_"),
                border, border, border, border)
        wInfo.addstr(1, 1, mouse)
        wInfo.addstr(2, 1, f"key: {c}")
        sInfo.writech(c)
        sInfo.draw()
        c_sus.draw()
        wInfo.refresh()

curses.wrapper(console)