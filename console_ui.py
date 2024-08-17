import curses.ascii
import os
import curses
import string

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _curses import _CursesWindow
    CursesWindowType = _CursesWindow
else:
    from typing import Any
    CursesWindowType = Any

# For Win10 at least
if os.name == "nt":
    KEY_BACKSPACE = 8
else:
    KEY_BACKSPACE = curses.KEY_BACKSPACE



el = "\r"
nl = "\n"

class ui_component():
    def __init__(self,
                 x: int,
                 y: int,
                 width: int,
                 heigth: int,
                 window: CursesWindowType,
                 enabled: bool = True,
                 activeColorPair: int = 0,
                 defaultColorPair: int = 0,
                 disabledColorPair: int = 0) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.heigth = heigth
        self.win = window
        self._enabled = enabled
        self.activeColorPair = activeColorPair
        self.defaultColorPair = defaultColorPair
        self.disabledColorPair = disabledColorPair

        self._active = False
    
    def __new__(cls, comp, *args, **kwargs):
        if cls.__base__ == ui_component:
            if not isinstance(comp, ui_component):
                raise TypeError(f"First parameter for component has to be an instance of {ui_component}")
            ui_component.__init__(cls, **dict(zip(ui_component.__init__.__code__.co_varnames[1:], comp.__dict__.values())))
        return super().__new__(cls)
    
    def _draw_default(self):
        pass

    def _draw_active(self):
        pass

    def _draw_disabled(self):
        pass

    def draw(self):
        if self._enabled:
            if self._active:
                self._draw_active()
                return
            self._draw_default()
        else:
            self._draw_disabled()
    
    def is_at_coordinates_xy(self,
                          x: int,
                          y: int) -> bool:
        return self.y >= y >= self.y + self.heigth and self.x <= x <= self.x + self.width
    
    # For height == 1
    def is_at_coordinates_x(self,
                          x: int,
                          y: int) -> bool:
        return y == self.y and self.x <= x <= self.x + self.width
    
    # For width == 1
    def is_at_coordinates_y(self,
                          x: int,
                          y: int) -> bool:
        return self.y >= y >= self.y + self.heigth and x == self.x
    
    def click(self,
              x: int,
              y: int):
        if self.is_at_coordinates_x(x, y):
            self._active = True
            return
        self._active = False
        
class checkBox(ui_component):
    def __init__(self,
                 comp: ui_component,
                 label: str = "",) -> None:
        self.label = label
        self.width = len(self.label) + 3

    def _draw_default(self):

            drawStr = self.label + "[ ]"
            if len(drawStr) == 0 and self.label:
                drawStr = self.label

            if self.defaultColorPair:
                self.win.addstr(self.y, self.x, drawStr, curses.color_pair(self.defaultColorPair))
            else:
                self.win.addstr(self.y, self.x, drawStr)

    def _draw_active(self):
            drawStr = self.label + "[X]"

            if self.activeColorPair:
                self.win.addstr(self.y, self.x, drawStr, curses.color_pair(self.activeColorPair))
            else:
                self.win.addstr(self.y, self.x, drawStr)

    def click(self,
              x: int,
              y: int):
        if self.is_at_coordinates_x(x, y):
            if self._active:
                self._active = False
                return
            self._active = True

class stringField(ui_component):
    def __init__(self,
                 comp: ui_component,
                 default: str = None,
                 inputFilter: callable = curses.ascii.isalpha) -> None:
        self.default = default
        self.string = ""
        self.filter = inputFilter

    def _draw_default(self):
            drawStr = self.string
            if len(drawStr) == 0 and self.default:
                drawStr = self.default

            if len(drawStr) < self.width:
                drawStr += "_" * (self.width - len(drawStr))

            if self.defaultColorPair:
                self.win.addstr(self.y, self.x, drawStr, curses.color_pair(self.defaultColorPair))
            else:
                self.win.addstr(self.y, self.x, drawStr)

    def _draw_active(self):
            drawStr = self.string
            if len(drawStr) < self.width:
                drawStr += "<"
                drawStr += "_" * (self.width - len(drawStr))

            if self.activeColorPair:
                self.win.addstr(self.y, self.x, drawStr, curses.color_pair(self.activeColorPair))
            else:
                self.win.addstr(self.y, self.x, drawStr)

    def writech(self,
                c: int):
        if self._active:
            if len(self.string) < self.width and (not self.filter or self.filter(c)):
                self.string += chr(c)

            if c == KEY_BACKSPACE and len(self.string) > 0:
                self.string = self.string[:-1]

            if c == 10:
                self._active = False


def console(screen: CursesWindowType):
    curses.start_color()
    curses.init_pair( 1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair( 3, curses.COLOR_YELLOW, curses.COLOR_WHITE)

    wInfo = curses.newwin(6, curses.COLS, 0, 0)
    sInfo = stringField(ui_component(1, 0, 20, 1, wInfo, activeColorPair = 1), "Sus")
    c_sus = checkBox(ui_component(1, 3, 20, 1, wInfo, activeColorPair = 1), "Impostor")
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