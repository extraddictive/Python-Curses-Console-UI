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

        self.update_boudary_check(width, heigth)
        self._active = False
    
    def __new__(cls, comp, *args, **kwargs):
        instance = super().__new__(cls)
        if cls.__base__ == ui_component:
            if not isinstance(comp, ui_component):
                raise TypeError(f"First parameter for component has to be an instance of {ui_component}")
            ui_component.__init__(instance, **dict(zip(ui_component.__init__.__code__.co_varnames[1:], comp.__dict__.values())))
        return instance
    
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
    
    def update_boudary_check(self,
                             width: int,
                             heigth: int):
        if heigth == 1:
            self.check_bounds = self.is_at_coordinates_x
        elif width == 1:
            self.check_bounds = self.is_at_coordinates_y
        else:
            self.check_bounds = self.is_at_coordinates_xy
        
    def resize(self,
               width: int,
               heigth: int):
        self.update_boudary_check(width, heigth)
        
        self.width = width
        self.heigth = heigth

    def is_at_coordinates_xy(self,
                          x: int,
                          y: int) -> bool:
        return self.y >= y >= self.y + self.heigth and self.x <= x <= self.x + self.width
    
    
    def is_at_coordinates_x(self,
                          x: int,
                          y: int) -> bool:
        "For height == 1"
        return y == self.y and self.x <= x <= self.x + self.width
    

    def is_at_coordinates_y(self,
                          x: int,
                          y: int) -> bool:
        "For width == 1"
        return self.y >= y >= self.y + self.heigth and x == self.x
    
    def click(self,
              x: int,
              y: int):
        if self.check_bounds(x, y):
            self._active = True
            return
        self._active = False
        
class Check_Box(ui_component):
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
        if self.check_bounds(x, y):
            if self._active:
                self._active = False
                return
            self._active = True

class Input_Box(ui_component):
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

class App():
    def __init__(self) -> None:
        self.scr = curses.initscr()

        curses.savetty()
        self.is_running = False

        curses.curs_set(0)
        curses.mousemask(1)

        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho()
        curses.cbreak()

        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        self.scr.keypad(1)

        # Start color, too.  Harmless if the terminal doesn't have
        # color; user can test with has_color() later on.  The try/catch
        # works around a minor bit of over-conscientiousness in the curses
        # module -- the error return from C start_color() is ignorable.
        try:
            curses.start_color()
            curses.init_pair( 1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair( 3, curses.COLOR_YELLOW, curses.COLOR_WHITE)
        except:
            pass
    
    def __del__(self):
        curses.resetty()
        curses.endwin()

    
    def run(self):
        self.is_running = True
        self._loop()

    def init_screen(self,
                    scr: CursesWindowType):
        curses.start_color()
        curses.init_pair( 1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair( 3, curses.COLOR_YELLOW, curses.COLOR_WHITE)

        curses.curs_set(0)
        curses.cbreak()
        curses.mousemask(1)

        scr.keypad(1)
        self.scr = scr

    def update(self,
               key: int):
        pass

    def _loop(self):
        self.update(0)
        while self.is_running:
            c = self.scr.getch()
            self.update(c)