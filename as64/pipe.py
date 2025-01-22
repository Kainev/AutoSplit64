# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from typing import Optional

import win32file
import win32pipe
import win32event

import pywintypes

import asyncio

from utils.log import get_logger
logger = get_logger(__name__)


class PipeError(Exception):
    """Base exception class for Pipe-related errors."""
    pass

class PipeConnectionError(PipeError):
    """Raised when a connection to the pipe fails."""
    pass

class PipeReadError(PipeError):
    """Raised when reading from the pipe fails."""
    pass

class PipeWriteError(PipeError):
    """Raised when writing to the pipe fails."""
    pass

class AsyncPipe:
    """
    A named pipe wrapper using asynchronous (overlapped) I/O on Windows.
    This class provides a header-based read mechanism and a raw write mechanism.
    """

    def __init__(self, name: str):
        """
        :param name: The name of the pipe
        """
        self.name = name
        self.pipe = None
        self.buffer = ""

    async def create(self):
        """
        Create the named pipe with overlapped I/O.
        Raises PipeConnectionError if creation fails.
        """
        try:
            self.pipe = win32pipe.CreateNamedPipe(
                self.name,
                win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED,
                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                1,      # Max instances
                4096,   # Out buffer size
                4096,   # In buffer size
                0,      # Default timeout
                None    # Default security attributes
            )
            logger.debug(f"[AsyncPipe.create] Created named pipe: {self.name}")
        except pywintypes.error as e:
            logger.error(f"[AsyncPipe.create] Failed to create pipe {self.name}: {e}")
            raise PipeConnectionError(f"[AsyncPipe.create] Failed to create pipe {self.name}: {e}") from e

    async def connect(self):
        """
        Wait for a client to connect to the pipe.
        Raises PipeConnectionError if connection fails.
        """
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                win32pipe.ConnectNamedPipe,
                self.pipe,
                None
            )
            logger.debug(f"[AsyncPipe.connect] Pipe connected: {self.name}")
        except pywintypes.error as e:
            logger.error(f"[AsyncPipe.connect] Failed to connect pipe {self.name}: {e}")
            raise PipeConnectionError(f"[AsyncPipe.connect] Failed to connect pipe {self.name}: {e}") from e

    async def _read_exactly(self, num_bytes: int) -> bytes:
        """
        Asynchronously read num_bytes from the pipe.
        Raises PipeReadError if reading fails or if the pipe is broken.
        """
        overlapped = pywintypes.OVERLAPPED()
        event = win32event.CreateEvent(None, True, False, None)
        overlapped.hEvent = event

        try:
            _, data = win32file.ReadFile(self.pipe, num_bytes, overlapped)

            await asyncio.get_event_loop().run_in_executor(
                None,
                win32event.WaitForSingleObject,
                overlapped.hEvent,
                win32event.INFINITE
            )
            logger.debug(f"[AsyncPipe._read_exactly] Read {num_bytes} bytes from {self.name}")
            return bytes(data)

        except pywintypes.error as e:
            if e.winerror == 109:  # ERROR_BROKEN_PIPE
                logger.error("[AsyncPipe._read_exactly] Broken pipe while reading.")
                raise PipeReadError("Pipe connection closed by the client.") from e
            else:
                logger.error(f"[AsyncPipe._read_exactly] Failed to read from {self.name}: {e}")
                raise PipeReadError(f"Failed to read from pipe {self.name}: {e}") from e

    async def read(self) -> list[str]:
        """
        Read data using a header-based protocol:
          1) Read 8 byte header (body length).
          2) Read 'body_length' bytes for the message body.
        Returns a list of messages (usually 1 message).
        Raises PipeReadError if reading fails.
        """
        messages = []
        try:
            while True:
                # 1
                header_data = await self._read_exactly(8)
                try:
                    header_str = header_data.decode("utf-8", errors="ignore").strip()
                    body_length = int(header_str)
                    logger.debug(f"[AsyncPipe.read] Parsed body length = {body_length}")
                except ValueError:
                    logger.debug(f"[AsyncPipe.read] Invalid header received: {header_data.hex()}")
                    continue

                # 2
                body_data = await self._read_exactly(body_length)
                try:
                    message = body_data.decode("utf-8")
                    logger.debug(f"[AsyncPipe.read] Decoded message: {message}")
                    messages.append(message)
                except UnicodeDecodeError:
                    logger.debug(f"[AsyncPipe.read] Invalid UTF-8 discarded: {body_data.hex()}")
                    continue

                if messages:
                    return messages

        except PipeReadError as e:
            logger.debug(f"[AsyncPipe.read] Pipe read error: {e}")
            return messages
        except Exception as e:
            logger.debug(f"[AsyncPipe.read] Unexpected error: {e}")
            return messages

    async def write(self, payload: str):
        """
        Write data to the pipe
        Raises PipeWriteError if the pipe is broken or writing fails.
        """
        overlapped = pywintypes.OVERLAPPED()
        event = win32event.CreateEvent(None, True, False, None)
        overlapped.hEvent = event

        payload_bytes = payload.encode("utf-8")

        try:
            win32file.WriteFile(self.pipe, payload_bytes, overlapped)

            await asyncio.get_event_loop().run_in_executor(
                None,
                win32event.WaitForSingleObject,
                overlapped.hEvent,
                win32event.INFINITE
            )
            logger.debug(f"[AsyncPipe.write] Wrote payload to {self.name}: {payload}")

        except pywintypes.error as e:
            if e.winerror in (232, 109):  # ERROR_NO_DATA, ERROR_BROKEN_PIPE
                logger.debug("[AsyncPipe.write] Broken pipe while writing.")
                raise PipeWriteError("Pipe connection closed by the client.") from e
            else:
                logger.debug(f"[AsyncPipe.write] Failed to write to {self.name}: {e}")
                raise PipeWriteError(f"Failed to write to pipe {self.name}: {e}") from e
        except Exception as e:
            logger.debug(f"[AsyncPipe.write] Unexpected error: {e}")
            raise PipeWriteError(f"Unexpected error during write to {self.name}: {e}") from e

    async def close(self):
        """
        Close the pipe.
        Disconnects any open connection and closes the handle.
        """
        if self.pipe:
            try:
                win32pipe.DisconnectNamedPipe(self.pipe)
            except pywintypes.error as e:
                logger.debug(f"[AsyncPipe.close] Error disconnecting pipe {self.name}: {e}")
            finally:
                win32file.CloseHandle(self.pipe)
                self.pipe = None
                logger.debug(f"[AsyncPipe.close] Pipe closed: {self.name}")



class Pipe:
    """Legacy class to manage named pipe communication"""

    def __init__(self, name):
        self.name = name
        self.pipe = None

    def create(self):
        """Create the named pipe."""
        try:
            self.pipe = win32pipe.CreateNamedPipe(
                self.name,
                win32pipe.PIPE_ACCESS_DUPLEX,
                win32pipe.PIPE_TYPE_MESSAGE |
                win32pipe.PIPE_READMODE_MESSAGE |
                win32pipe.PIPE_WAIT,
                1,
                65536,
                65536,
                0,
                None 
            )
            
            logger.info(f"Named pipe created: {self.name}")
        except pywintypes.error as e:
            error_code, func_name, error_message = e.args
            logger.exception(
                f"PyWin32 error while creating named pipe {self.name}: "
                f"[Error {error_code}] {func_name} - {error_message}"
            )
            raise PipeConnectionError(
                f"Failed to create named pipe {self.name}: [Error {error_code}] {error_message}"
            ) from e
        except Exception as e:
            logger.exception(f"Unexpected error while creating named pipe {self.name}: {e}")
            raise PipeConnectionError(f"Unexpected error while creating named pipe {self.name}") from e
        
    def connect(self):
        """Connect to the named pipe."""
        try:
            win32pipe.ConnectNamedPipe(self.pipe, None)
            logger.info(f"Connected to named pipe: {self.name}")
        except pywintypes.error as e:
            # Extract error details from pywintypes.error
            error_code, func_name, error_message = e.args
            logger.error(
                f"PyWin32 error while connecting to pipe {self.name}: "
                f"[Error {error_code}] {func_name} - {error_message}", exc_info=True
            )
            raise PipeConnectionError(
                f"Failed to connect to named pipe {self.name}: [Error {error_code}] {error_message}"
            ) from e
        except Exception as e:
            logger.exception(f"Unexpected error while connecting to pipe {self.name}: {e}", exc_info=True)
            raise PipeConnectionError(f"Unexpected error while connecting to pipe {self.name}") from e



    def peek(self) -> bool:
        """Check if there is data available in the pipe."""
        try:
            _, _, total_bytes = win32pipe.PeekNamedPipe(self.pipe, 0)
            logger.debug(f"Peeked pipe {self.name}: {total_bytes} bytes available")
            return total_bytes > 0
        except pywintypes.error as e:
            error_code, func_name, error_message = e.args
            logger.error(
                f"PyWin32 error while peeking pipe {self.name}: "
                f"[Error {error_code}] {func_name} - {error_message}", exc_info=True
            )
            raise PipeReadError(
                f"Failed to peek pipe {self.name}: [Error {error_code}] {error_message}"
            ) from e
        except Exception as e:
            logger.exception(f"Unexpected error while peeking pipe {self.name}: {e}", exc_info=True)
            raise PipeReadError(f"Unexpected error while peeking pipe {self.name}") from e

        
    def read(self, peek: bool = True) -> Optional[str]:
        """Read data from the pipe."""
        try:
            if peek and not self.peek():
                return None

            _, data = win32file.ReadFile(self.pipe, 65536)
            data = data.decode("utf-8").strip()
            
            logger.debug(f"Read from pipe {self.name}: {data}")
            
            return data
        except pywintypes.error as e:
            error_code, func_name, error_message = e.args
            logger.error(
                f"PyWin32 error while reading from pipe {self.name}: "
                f"[Error {error_code}] {func_name} - {error_message}", exc_info=True
            )
            raise PipeReadError(
                f"Failed to read from pipe {self.name}: [Error {error_code}] {error_message}"
            ) from e
        except Exception as e:
            logger.exception(f"Unexpected error while reading from pipe {self.name}: {e}", exc_info=True)
            raise PipeReadError(f"Unexpected error while reading from pipe {self.name}") from e


    def write(self, payload: str):
        """Write data to the pipe."""
        try:
            win32file.WriteFile(self.pipe, payload.encode("utf-8"))
            logger.debug(f"Wrote to pipe {self.name}: {payload}")
        except pywintypes.error as e:
            error_code, func_name, error_message = e.args
            logger.error(
                f"PyWin32 error while writing to pipe {self.name}: "
                f"[Error {error_code}] {func_name} - {error_message}", exc_info=True
            )
            raise PipeWriteError(
                f"Failed to write to named pipe {self.name}: [Error {error_code}] {error_message}"
            ) from e
        except Exception as e:
            logger.exception(f"Unexpected error while writing to pipe {self.name}: {e}", exc_info=True)
            raise PipeWriteError(f"Unexpected error while writing to pipe {self.name}") from e

    def close(self):
        """Close the pipe."""
        if self.pipe:
            try:
                win32pipe.DisconnectNamedPipe(self.pipe)
                logger.debug(f"Disconnected named pipe: {self.name}")
            except pywintypes.error as e:
                error_code, func_name, error_message = e.args
                logger.error(
                    f"PyWin32 warning while disconnecting pipe {self.name}: "
                    f"[Error {error_code}] {func_name} - {error_message}", exc_info=True
                )
            except Exception as e:
                logger.exception(f"Unexpected error while disconnecting pipe {self.name}: {e}", exc_info=True)

            try:
                win32file.CloseHandle(self.pipe)
                logger.debug(f"Closed handle for pipe: {self.name}")
            except pywintypes.error as e:
                error_code, func_name, error_message = e.args
                logger.error(
                    f"PyWin32 warning while closing pipe handle {self.name}: "
                    f"[Error {error_code}] {func_name} - {error_message}", exc_info=True
                )
            except Exception as e:
                logger.exception(f"Unexpected error while closing pipe handle {self.name}: {e}", exc_info=True)
            finally:
                # Ensure the handle is set to None regardless of errors
                self.pipe = None
                logger.debug(f"Pipe handle cleared for {self.name}")
        else:
            logger.debug(f"Close called, but pipe {self.name} is already None")
