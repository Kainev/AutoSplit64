import socket
import select

from . import config


def connect(ls_socket) -> bool:
    try:
        ls_socket.connect((config.get("connection", "ls_host"), config.get("connection", "ls_port")))
    except:
        return False


def disconnect(ls_socket) -> None:
    ls_socket.close()


def check_connection(ls_socket) -> bool:
    if split_index(ls_socket) is False:
        return False
    else:
        return True


def init_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send(ls_socket, command) -> None:
    ls_socket.send(command.encode('utf-8'))


def split(ls_socket) -> None:
    send(ls_socket, "startorsplit\r\n")


def reset(ls_socket) -> None:
    send(ls_socket, "reset\r\n")


def skip(ls_socket) -> None:
    send(ls_socket, "skipsplit\r\n")


def undo(ls_socket) -> None:
    send(ls_socket, "unsplit\r\n")


def split_index(ls_socket):
    try:
        ls_socket.send("getsplitindex\r\n".encode('utf-8'))
    except:
        return False

    readable = select.select([ls_socket], [], [], 0.5)
    if readable[0]:
        try:
            data = (ls_socket.recv(1000)).decode("utf-8")
            if not isinstance(data, bool):
                return int(data)
            else:
                return False
        except:
            return False
    else:
        return False
