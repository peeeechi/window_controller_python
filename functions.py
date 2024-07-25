import ctypes
import time
from numpy import abs
from typing import Optional, Callable
from pydantic import BaseModel

class Point(BaseModel):
    x: int
    y: int

class Rect(BaseModel):
    left: int
    '''
    矩形の左上隅のx座標を指定します
    '''
    top: int
    '''
    矩形の左上隅のy座標を指定します
    '''
    right: int
    '''
    矩形の右下隅のx座標を指定します
    '''
    bottom: int
    '''
    矩形の右下隅のy座標を指定します
    '''
    @property
    def height(self) -> int:
        '''
        矩形の高さを取得します
        '''
        return abs(self.top - self.bottom)
    @property
    def width(self) -> int:
        '''
        矩形の幅を取得します
        '''
        return abs(self.right - self.left)
    @property
    def center(self) -> Point:
        return Point(x=int(self.left + (self.width / 2.0)), y=int(self.top + (self.height / 2.0)))

class WindowsApi(object):
    user32 = ctypes.WinDLL("user32")
    class POINT(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_int32),
            ("y", ctypes.c_int32),
        ]

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_int32),
            ("top", ctypes.c_int32),
            ("right", ctypes.c_int32),
            ("bottom", ctypes.c_int32),
        ]


    GetCursorPos = user32.GetCursorPos
    GetCursorPos.restype = ctypes.c_bool
    GetCursorPos.argtypes = (ctypes.POINTER(POINT),)

    # EnumWindows
    # https://docs.microsoft.com/ja-jp/windows/win32/api/winuser/nf-winuser-enumwindows
    EnumWindowProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    EnumWindows = user32.EnumWindows
    EnumWindows.restype = ctypes.c_bool
    EnumWindows.argtypes= (EnumWindowProc, ctypes.c_void_p)

    # EnumChildWindows
    # https://docs.microsoft.com/ja-jp/windows/win32/api/winuser/nf-winuser-enumchildwindows
    EnumChildWindows = user32.EnumChildWindows
    EnumChildWindows.restype = ctypes.c_bool
    EnumChildWindows.argtypes= (ctypes.c_void_p, EnumWindowProc, ctypes.c_void_p)
    
    GetWindowRect = user32.GetWindowRect
    GetWindowRect.restype = ctypes.c_bool
    GetWindowRect.argtypes = (ctypes.c_void_p, ctypes.POINTER(RECT))

def get_cursor_pos() -> Optional[Point]:
    p = WindowsApi.POINT()
    if WindowsApi.GetCursorPos(p):
        return Point(x=p.x, y=p.y)
    else:
        return None

enum_window_proc = Callable[[Optional[int], Optional[int]], bool]
def enum_windows(cb: enum_window_proc,  lParam: Optional[str]):
    '''
    各ウィンドウへのハンドルをアプリケーション定義のコールバック関数に渡すことにより、画面上のすべてのトップレベルウィンドウを列挙します\n
    EnumWindowsは、最後の最上位ウィンドウが列挙されるか、コールバック関数がFALSEを返すまで続きます\n
    https://docs.microsoft.com/ja-jp/windows/win32/api/winuser/nf-winuser-enumwindows
    '''
    WindowsApi.EnumWindows(WindowsApi.EnumWindowProc(cb), lParam)

def get_window_rect(hWnd: int)-> Optional[Rect]:
    '''
    指定されたウィンドウの外接する四角形の寸法を取得します \n
    寸法は、画面の左上隅を基準にした画面座標で示されます \n
    https://docs.microsoft.com/ja-jp/windows/win32/api/winuser/nf-winuser-getwindowrect
    '''
    rect = WindowsApi.RECT()
    if WindowsApi.GetWindowRect(hWnd, rect):
        return Rect(
            left=rect.left,
            top=rect.top,
            right=rect.right,
            bottom=rect.bottom
        )
    else:
        None 

def test():

    # for i in range(5):
    #     p = get_cursor_pos()
    #     if p is not None:
    #         print(f"x = {p.x}, y = {p.y}")
    #     time.sleep(1.0)

    def cb(hWnd, lParam) -> bool:
        print(f"hWnd: {hWnd}({type(hWnd)})")
        print(f"lParam: {lParam}({type(lParam)})")
        r = get_window_rect(hWnd)
        print(f"rect: [{r.left}, {r.top}, {r.right}, {r.bottom}], center = {r.center}")
        return True
    enum_windows(cb, None)


test()