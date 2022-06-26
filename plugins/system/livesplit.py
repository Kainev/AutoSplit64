# Plugin
from as64.plugin import SplitPlugin, Definition

# Python
import socket
import select

# AS64
from as64 import GameStatus, EventEmitter, config 
from as64.constants import Event

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

        self._game_status = None
        self._emitter: EventEmitter = None
        
        
    def initialize(self, ev):
        self._host = config.get("connection", "host")
        self._port = config.get("connection", "port")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
        self._connect()
        
        self._game_status: GameStatus = ev.status
        self._emitter: EventEmitter = ev.emitter

    def split(self):
        self._send(LiveSplit.Command.SPLIT)
        self._set_split_index(self._game_status.current_split_index + 1)
        self._emitter.emit(Event.SPLIT)
    
    def skip(self):
        self._send(LiveSplit.Command.SKIP)
        self._set_split_index(self._game_status.current_split_index + 1)
        self._emitter.emit(Event.SKIP)
    
    def undo(self):
        self._send(LiveSplit.Command.UNDO)
        self._set_split_index(self._game_status.current_split_index - 1)
        self._emitter.emit(Event.UNDO)
    
    def reset(self):
        self._send(LiveSplit.Command.RESET)
        self._set_split_index(0)
        self._emitter.emit(Event.RESET)
        
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
    
    def execute(self, ev):
        ls_index = self.index()
        
        if ls_index != self._game_status.current_split_index:
            self._set_split_index(ls_index)
            self._game_status.external_split_update = True
            self._emitter.emit(Event.EXTERNAL_SPLIT_UPDATE)
    
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
        
    def _set_split_index(self, index):
        self._game_status.current_split_index = index
        self._game_status.current_split = self._game_status.route.splits[self._game_status.current_split_index]
        self._game_status.external_split_update = False