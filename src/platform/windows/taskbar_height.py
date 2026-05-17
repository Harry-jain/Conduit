"""Windows taskbar metrics."""

from __future__ import annotations

import ctypes
from ctypes import wintypes


def get_taskbar_height() -> int:
    """Return taskbar height using SHAppBarMessage with fallback."""
    try:
        shell32 = ctypes.WinDLL("shell32", use_last_error=True)
        user32 = ctypes.WinDLL("user32", use_last_error=True)

        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", wintypes.LONG),
                ("top", wintypes.LONG),
                ("right", wintypes.LONG),
                ("bottom", wintypes.LONG),
            ]

        class APPBARDATA(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("hWnd", wintypes.HWND),
                ("uCallbackMessage", wintypes.UINT),
                ("uEdge", wintypes.UINT),
                ("rc", RECT),
                ("lParam", ctypes.c_int),
            ]

        ABM_GETTASKBARPOS = 0x00000005
        ABE_LEFT = 0
        ABE_TOP = 1
        ABE_RIGHT = 2
        ABE_BOTTOM = 3

        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        ok = shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(abd))
        if ok:
            if abd.uEdge in (ABE_TOP, ABE_BOTTOM):
                return max(int(abd.rc.bottom - abd.rc.top), 0)
            if abd.uEdge in (ABE_LEFT, ABE_RIGHT):
                return max(int(abd.rc.right - abd.rc.left), 0)

        SPI_GETWORKAREA = 0x0030
        work_area = RECT()
        ok = user32.SystemParametersInfoW(
            SPI_GETWORKAREA,
            0,
            ctypes.byref(work_area),
            0,
        )
        if ok:
            screen_h = int(user32.GetSystemMetrics(1))
            work_h = int(work_area.bottom - work_area.top)
            if screen_h > work_h > 0:
                return screen_h - work_h
    except (AttributeError, OSError, ValueError):
        pass
    return 48
