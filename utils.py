import sys

try:
    import termios
except ImportError:
    termios = None


def clear_input_buffer():
    if termios is None:
        return

    try:
        termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
    except termios.error:
        pass

