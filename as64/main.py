# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

import threading
import logging
import queue
import json

import asyncio
from pymitter import EventEmitter

from as64 import config, log, api
from as64.core import AS64
from as64.plugins import PluginManager
from as64.ipc import rpc
from as64.ipc.pipe import (
    AsyncPipe,
    PipeError,
    PipeWriteError,
    PipeReadError,
)

logger = logging.getLogger(__name__)


PIPE_NAME = r'\\.\pipe\AutoSplit64'


class AS64Coordinator:
    def __init__(self, pipe_name: str):
        self.pipe = AsyncPipe(pipe_name)

        # Incoming messages to AS64 processing thread
        self.in_queue: "queue.Queue[dict]" = queue.Queue()
        # Outgoing messages from processing thread to pipe_writer
        self.out_queue: asyncio.Queue = asyncio.Queue()

        self.stop_event = asyncio.Event()

        self.as64_thread: threading.Thread = None
        self.as64_stop_event = threading.Event()
        
        self.plugin_manager = PluginManager("plugins")
        self.plugin_manager.load_plugins()
                
        # Event loop reference
        self.event_loop: asyncio.AbstractEventLoop = None
        
        # Emitter
        self.emitter = EventEmitter()
        
        # Register emitter with API
        api.emitter._emitter = self.emitter
        
        # Requests
        self.pending_requests = {}

    async def pipe_reader(self):
        """Asynchronously reads messages from the pipe."""
        try:
            while not self.stop_event.is_set():
                messages = await self.pipe.read()
                for message in messages:
                    try:
                        data = json.loads(message)
                        logger.debug(f"[AS64Coordinator.pipe_reader] Received message: {data}")

                        if "rpc" in data:
                            await self.handle_rpc(data)
                            continue
                        else:
                            self.in_queue.put(data)

                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON received: {message}")

        except PipeReadError as e:
            logger.error(f"[AS64Coordinator.pipe_reader] Pipe read error: {e}")
        except PipeError as e:
            logger.error(f"[AS64Coordinator.pipe_reader] Pipe error: {e}")
        except Exception as e:
            logger.exception(f"[AS64Coordinator.pipe_reader] Unexpected error: {e}")
        finally:
            logger.debug("[AS64Coordinator.pipe_reader] Exiting read loop.")

    async def pipe_writer(self):
        """
        Asynchronously writes messages to the pipe.
        Awaits on the process_out_queue for messages from the AS64 processing thread
        and then sends them to the pipe.
        """
        try:
            while not self.stop_event.is_set():
                try:
                    item = await self.out_queue.get()
                    if item is None:
                        logger.debug("[AS64Coordinator.pipe_writer] Received shutdown sentinel.")
                        break

                    serialized_payload = json.dumps(item)
                    await self.pipe.write(serialized_payload)
                    
                    logger.debug(f"[AS64Coordinator.pipe_writer] Sent message: {serialized_payload}")
                except PipeWriteError as e:
                    logger.error(f"[AS64Coordinator.pipe_writer] Pipe write error: {e}")
                except Exception as e:
                    logger.exception(f"[AS64Coordinator.pipe_writer] Unexpected error: {e}")
        finally:
            logger.info("[AS64Coordinator.pipe_writer] Exiting write loop.")
            
    async def handle_rpc(self, data):
        """Handle the RPC message (dispatcher call + sending the response)."""
        proc_name = data["rpc"]
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
        
        request_id = data.get("requestId")

        response = {"replyTo": request_id} if request_id else {}

        result, error = await rpc.call(proc_name, args, kwargs)
        if error is not None:
            response["error"] = error
        else:
            response["result"] = result

        if request_id:
            try:
                await self.pipe.write(json.dumps(response))
            except PipeWriteError as e:
                logger.error(f"[handle_rpc] Pipe write error: {e}")

    def enqueue_message(self, message: dict):
        """
        Thread-safe method to enqueue a message to be written to the pipe.
        This method can be called from the AS64 processing thread.
        :param message: The message dictionary to send.
        """
        if self.event_loop is None:
            logger.error("[AS64Coordinator.enqueue_message] Event loop not set.")
            return

        self.event_loop.call_soon_threadsafe(self.out_queue.put_nowait, message)
        logger.debug(f"[AS64Coordinator.enqueue_message] Enqueued message for writing: {message}")

    def start_as64(self):
        """
        Start the AS64 processing thread
        """
        if self.as64_thread and self.as64_thread.is_alive():
            logger.warning("[AS64Coordinator.start_as64] AS64 thread is already running.")
            return False

        logger.info("[AS64Coordinator.start_as64] Starting AS64 processing thread.")
        self.as64_stop_event.clear()
        self.as64_thread = threading.Thread(
            target=self.as64_loop,
            args=(),
            daemon=True
        )
        self.as64_thread.start()
        
        return True

    def stop_as64(self):
        """
        Stop the AS64 processing thread
        """
        if self.as64_thread and self.as64_thread.is_alive():
            logger.info("[AS64Coordinator.stop_as64] Stopping AS64 processing thread.")
            self.as64_stop_event.set()
            self.as64_thread.join()
            self.as64_thread = None
            logger.info("[AS64Coordinator.stop_as64] AS64 processing thread stopped.")
            
            return True
        else:
            logger.warning("[AS64Coordinator.stop_as64] AS64 thread is not running.")
            return False

    def as64_loop(self):
        """
        The main AS64 loop
        """
        logger.info("[AS64Coordinator.as64_loop] AS64 Loop started.")
        
        _as64 = AS64(self.plugin_manager, None)
        
        try:
            while not self.as64_stop_event.is_set():
                _as64.run()
        finally:
            logger.info("[AS64Coordinator.as64_loop] AS64 loop exiting.")

    async def run(self):
        """Main controller logic."""
        try:
            self.event_loop = asyncio.get_running_loop()

            await self.pipe.create()
            await self.pipe.connect()

            read_task = asyncio.create_task(self.pipe_reader())
            write_task = asyncio.create_task(self.pipe_writer())

            await asyncio.gather(read_task, write_task)

        except Exception as e:
            logger.exception(f"[AS64Coordinator.run] Controller encountered an error: {e}")
        finally:
            logger.info("[AS64Coordinator.run] Shutting down Controller.")
            self.stop_as64()
            
            self.stop_event.set()
            self.enqueue_message(None)  # Enqueue sentinel

            await self.pipe.close()
            

if __name__ == "__main__":
    log.configure_logging()
    config.load()

    controller = AS64Coordinator(PIPE_NAME)
    
    @rpc.register("as64.start")
    def start():
        return controller.start_as64()
    
    @rpc.register("as64.stop")
    def stop():
        return controller.stop_as64()
    
    try:
        asyncio.run(controller.run())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
