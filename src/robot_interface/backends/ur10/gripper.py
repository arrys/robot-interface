import socket

from robot_interface.interface import GripperCapabilities, GripperAdapter


class RobotiqGripperURAdapter(GripperAdapter):
    backend_name = "robotiq"

    def __init__(self, host: str, port: int = 63352):
        self.host = host
        self.port = port
        self._socket = None

    def connect(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(3)
        self._socket.connect((self.host, self.port))
        self._socket.sendall('SET ACT 1'.encode('utf-8'))
        self._socket.sendall('SET GTO 1'.encode('utf-8'))
        self._socket.sendall('SET SPE 255'.encode('utf-8'))
        self._socket.sendall('SET FOR 255'.encode('utf-8'))

    def disconnect(self) -> None:
        self._socket.close()

    def get_capabilities(self) -> GripperCapabilities:
        return GripperCapabilities(open=True, close=True, move=True, get_position=True, raw_command=False)

    def open(self) -> None:
        self.set_position(position=0)

    def close(self) -> None:
        self.set_position(position=255)

    def set_position(self, position: int) -> None:
        if not isinstance(position, int) or position < 0 or position > 255:
            raise ValueError("Position must be an integer between 0 (open) and 255 (closed)")
        s = self._socket
        command = f'SET POS {position}\n'.encode('utf-8')
        s.sendall(command)
        s.recv(2**10)

    @property
    def position(self) -> int:
        command = b'GET POS\n'
        self._socket.sendall(command)
        data = self._socket.recv(2 ** 10)
        response = data.decode('utf-8', errors='ignore').strip()
        if "POS" in response:
            pos = int(response.split()[-1])
            return pos
        raise RuntimeError("Failed to read position")
