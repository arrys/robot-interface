import socket
import time


def send_command(connection: socket.socket, command: str) -> str:
    connection.sendall((command + "\n").encode("ascii"))
    return connection.recv(1024).decode("ascii", errors="replace").strip()


def main() -> None:
    host = "192.168.1.200"
    port = 63352

    with socket.create_connection((host, port), timeout=3.0) as connection:
        connection.settimeout(2.0)
        print(send_command(connection, "GET STA"))
        print(send_command(connection, "SET ACT 1"))
        time.sleep(0.5)
        print(send_command(connection, "SET GTO 1"))
        print(send_command(connection, "SET SPE 255"))
        print(send_command(connection, "SET FOR 255"))
        print(send_command(connection, "SET POS 255"))  # close

if __name__ == "__main__":
    main()
