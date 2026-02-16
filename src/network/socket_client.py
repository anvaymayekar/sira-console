"""Socket client for connecting to Raspberry Pi."""

import socket
import threading
import struct
import json
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
import cv2
from .protocol import MessageType


class SocketClient(QObject):
    """TCP socket client for Pi communication."""

    # Qt signals for thread-safe GUI updates
    frame_received = pyqtSignal(np.ndarray)  # Camera frame
    telemetry_received = pyqtSignal(dict)  # Telemetry data
    connection_changed = pyqtSignal(bool)  # Connection state
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self):
        """Initialize socket client."""
        super().__init__()
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.receiver_thread: Optional[threading.Thread] = None
        self.host = ""
        self.port = 0

    def connect(self, host: str, port: int) -> bool:
        """
        Connect to Raspberry Pi server.

        Args:
            host: Pi IP address
            port: Port number

        Returns:
            True if connection successful
        """
        try:
            self.host = host
            self.port = port

            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)

            # Connect
            print(f"Connecting to {host}:{port}...")
            self.socket.connect((host, port))
            print("Connected!")

            # Start receiver thread
            self.running = True
            self.receiver_thread = threading.Thread(
                target=self._receive_loop, daemon=True, name="SocketReceiver"
            )
            self.receiver_thread.start()

            self.connection_changed.emit(True)
            return True

        except socket.timeout:
            self.error_occurred.emit("Connection timeout")
            return False
        except ConnectionRefusedError:
            self.error_occurred.emit("Connection refused - is Pi server running?")
            return False
        except Exception as e:
            self.error_occurred.emit(f"Connection failed: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from Pi."""
        print("Disconnecting...")
        self.running = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        self.connection_changed.emit(False)
        print("Disconnected")

    def is_connected(self) -> bool:
        """Check if connected."""
        return self.running and self.socket is not None

    def _receive_loop(self):
        """Continuously receive data from Pi (runs in thread)."""
        print("Receiver thread started")

        try:
            while self.running:
                # Read message header: [1 byte type][4 bytes length]
                header = self._recv_exact(5)
                if not header:
                    break

                # Unpack header
                msg_type, payload_length = struct.unpack("!BI", header)

                # Read payload
                payload = self._recv_exact(payload_length)
                if not payload:
                    break

                # Handle message based on type
                if msg_type == MessageType.FRAME:
                    self._handle_frame(payload)
                elif msg_type == MessageType.TELEMETRY:
                    self._handle_telemetry(payload)
                else:
                    print(f"Unknown message type: {msg_type}")

        except Exception as e:
            if self.running:
                print(f"Receive error: {e}")
                self.error_occurred.emit(f"Receive error: {str(e)}")
        finally:
            print("Receiver thread stopped")
            self.disconnect()

    def _recv_exact(self, num_bytes: int) -> bytes:
        """
        Receive exact number of bytes.

        Args:
            num_bytes: Number of bytes to receive

        Returns:
            Received bytes or empty if connection closed
        """
        data = b""
        while len(data) < num_bytes:
            try:
                chunk = self.socket.recv(num_bytes - len(data))
                if not chunk:
                    return b""
                data += chunk
            except socket.timeout:
                continue
            except Exception:
                return b""
        return data

    def _handle_frame(self, payload: bytes):
        """
        Decode and emit camera frame.

        Args:
            payload: JPEG encoded frame
        """
        try:
            # Decode JPEG
            nparr = np.frombuffer(payload, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                self.frame_received.emit(frame)
        except Exception as e:
            print(f"Frame decode error: {e}")

    def _handle_telemetry(self, payload: bytes):
        """
        Decode and emit telemetry data.

        Args:
            payload: JSON encoded telemetry
        """
        try:
            data = json.loads(payload.decode("utf-8"))
            self.telemetry_received.emit(data)
        except Exception as e:
            print(f"Telemetry decode error: {e}")

    def send_command(self, command: dict):
        """
        Send command to Pi.

        Args:
            command: Command dictionary
        """
        if not self.is_connected():
            self.error_occurred.emit("Not connected")
            return

        try:
            cmd_bytes = json.dumps(command).encode("utf-8")
            header = struct.pack("!BI", MessageType.COMMAND, len(cmd_bytes))
            self.socket.sendall(header + cmd_bytes)
        except Exception as e:
            self.error_occurred.emit(f"Send failed: {str(e)}")
