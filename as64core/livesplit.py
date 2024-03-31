import socket
import select
import win32file
import win32pipe
import time

from . import config

# Connect to LiveSplit and return socket
def connect() -> object:
    # Get connection type from config
    ls_connection_type = config.get("connection", "ls_connection_type")

    # Check if connection type is named pipe (0 indicates named pipe)
    if ls_connection_type == 0:
        # Get named pipe host from config. Name is always LiveSplit
        ls_pipe_path = "\\\\" + config.get("connection", "ls_pipe_host") + "\\pipe\\LiveSplit"
        try:
            # Connect to named pipe
            ls_socket = win32file.CreateFile(ls_pipe_path, win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, 0, None )
            # Set the pipe to byte mode
            win32pipe.SetNamedPipeHandleState(ls_socket, win32pipe.PIPE_READMODE_BYTE, None, None)
            return ls_socket
        except:
            return False
    # Check if connection type is TCP (1 indicates TCP)
    elif ls_connection_type == 1:
        try:
            # Initialize socket
            ls_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Get host and port from config and connect to host via TCP
            ls_socket.connect((config.get("connection", "ls_host"), config.get("connection", "ls_port")))
            return ls_socket
        except:
            return False
    else:
        return False


def disconnect(ls_socket) -> None:
    # Check if connection even exists
    if ls_socket is False:
        return
    ls_socket.close()


def check_connection(ls_socket) -> bool:
    # Check if connection has been established
    if (ls_socket == False):
        # print("Failed to connect to LiveSplit")
        return False
    # Check if communication is possible and response is received
    try:
        if split_index(ls_socket) is False:
            return False
        else:
            return True
    except:
        return False


def send(ls_socket, command) -> None:
    # Check if connection type is pipe or socket
    # If it is a socket:
    if isinstance(ls_socket, socket.socket):
        # print("Sending command to socket: " + command)
        # Send the command to the socket
        ls_socket.send(command.encode('utf-8'))
    # If it is a pipe:
    else:
        # print("Sending command to pipe: " + command)
        # Send the command to the pipe
        win32file.WriteFile(ls_socket, command.encode('utf-8'))


def split(ls_socket) -> None:
    send(ls_socket, "startorsplit\r\n")


def reset(ls_socket) -> None:
    send(ls_socket, "reset\r\n")


def skip(ls_socket) -> None:
    send(ls_socket, "skipsplit\r\n")


def undo(ls_socket) -> None:
    send(ls_socket, "unsplit\r\n")


def split_index(ls_socket):
    # Check if connection type is pipe or socket
    # If it is a socket:
    if isinstance(ls_socket, socket.socket):
        # Send the command to the socket
        try:
            ls_socket.send("getsplitindex\r\n".encode('utf-8'))
        except:
            # print("Failed to write to socket")
            raise Exception("Failed to write to socket")
        
        # Wait for response
        readable = select.select([ls_socket], [], [], 0.5)
        if readable[0]:
            try:
                data = (ls_socket.recv(1000)).decode("utf-8")
                # print("Data: " + data)
                if not isinstance(data, bool):
                    return int(data)
                else:
                    return False
            except:
                # print("Failed to read from socket")
                raise Exception("Failed to read from socket")
        else:
            return False
    # If it is a pipe:
    else:
        # Send the command to the pipe
        try:
            win32file.WriteFile(ls_socket, "getsplitindex\r\n".encode('utf-8'))
        except:
            # print("Failed to write to pipe")
            raise Exception("Failed to write to pipe")
        # Get current time
        start_time = time.time()
        # Set timeout to 0.5 seconds
        timeout = 0.5
        # Read from pipe until success or timeout
        while True:
            # Check if the timeout has occurred
            if time.time() - start_time > timeout:
                # print("Failed to read from pipe")
                raise Exception("Failed to read from pipe")
            # Peek at the pipe to see if there is data as it is non-blocking
            peek_data, available , _ = win32pipe.PeekNamedPipe(ls_socket, 1000)
            # If there is data available:
            if available > 0:
                # Read the data from the pipe
                data = win32file.ReadFile(ls_socket, 1000)[1].decode("utf-8")
                # print("Data: " + data)
                if not isinstance(data, bool):
                    return int(data)
                else:
                    return False