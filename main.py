import reconize
import nonogram
# from ctypes import windll
import win32api, win32con, win32gui
import time

def click_board(board,offset=(0,0),size=30):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 1:
                click(offset[0]+size*j,offset[1]+size*i)
                time.sleep(0.03)

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(0.03)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)


def getCursorPos():
    return win32api.GetCursorPos()

def findWindow():
    hwnd = win32gui.FindWindow(None, 'AnLink')
    if hwnd == 0:
        return None
    return hwnd

def getWindowRect(hwnd):
    return win32gui.GetWindowRect(hwnd)

def setForegroundWindow(hwnd):
    win32api.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
    win32gui.SetForegroundWindow(hwnd)

if __name__ == '__main__':
    hwnd = findWindow()
    setForegroundWindow(hwnd)
    l,t,r,b = getWindowRect(hwnd)
    offset = (int(l+(r-l)*0.4219),int(t+(b-t)*0.3509))
    size = int(0.02252*(b-t))
    c,r,e = reconize.get_board(15)
    solver = nonogram.NonogramSolver(
        ROWS_VALUES=r,
        COLS_VALUES=c,
        EXTRA = e,
    )
    click_board(solver.board, offset,size)
