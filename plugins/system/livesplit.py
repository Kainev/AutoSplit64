# Plugin
from as64.plugin import SplitPlugin, Definition

# Python
import socket
import select

# AS64
from as64 import config

class LiveSplitDefinition(Definition):
    NAME = "LiveSplit"
    VERSION = "1.0.0"


class LiveSplit(SplitPlugin):
    DEFINITION = LiveSplitDefinition
    
    class Command(object):
        SPLIT = "startorsplit\r\n"
        SKIP = "skipsplit\r\n"
        UNDO = "unsplit\r\n"
        RESET = "reset\r\n"
        INDEX = "getsplitindex\r\n"
        
        
    ENCODING = "utf-8"
       
    def __init__(self):
        self._socket: socket.socket = None
        self._host = None
        self._port = None
        
    def initialize(self):
        self._host = config.get("connection", "host")
        self._port = config.get("connection", "port")
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
        self._connect()
    
    def split(self):
        self._send(LiveSplit.Command.SPLIT)
    
    def skip(self):
        self._send(LiveSplit.Command.SKIP)
    
    def undo(self):
        self._send(LiveSplit.Command.UNDO)
    
    def reset(self):
        self._send(LiveSplit.Command.RESET)
        
    def index(self):
        try:
            self._send(LiveSplit.Command.INDEX)
        except:
            return False
        
        readable = select.select([self._socket], [], [], 0.5)
        
        if readable[0]:
            try:
                data = (self._socket.recv(1000)).decode(LiveSplit.ENCODING)
                
                if not isinstance(data, bool):
                    return int(data)
            except:
                pass
            
        return False
    
    def _connect(self):
        try:
            self._socket.connect((self._host, self._port))
        except ConnectionRefusedError:
            print("LiveSplit Connection Refused")
        except TypeError:
            print("LiveSplit Configuration Error")
        except socket.timeout:
            print("LiveSplit Timed Out")
        except socket.error as e:
            print("LiveSplit Error:", e)
        # except Exception:
        #     pass

    def _send(self, command) -> None:
        self._socket.send(command.encode(LiveSplit.ENCODING))
        
        # TODO: try except socket.timeout, socket.error (?)