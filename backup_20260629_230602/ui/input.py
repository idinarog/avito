import sys
import termios
import tty

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)

        if ch == "\x1b":
            ch2 = sys.stdin.read(2)
            if ch2 == "[A":
                return "UP"
            if ch2 == "[B":
                return "DOWN"

        if ch == "\n":
            return "ENTER"

        return ch

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)