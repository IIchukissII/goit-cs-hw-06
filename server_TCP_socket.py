
import socket
from concurrent import futures as cf
import json
import mongo_interface as mi

TCP_IP = "localhost"
TCP_PORT = 8080


def run_server(ip, port):
    def handle(sock: socket.socket, address: str):
        print(f"Connection established {address}")
        data = ""
        while True:
            received = sock.recv(1024)
            if not received:
                break
            data = data + received.decode()
            sock.send(received)
        data = json.loads(data)
        print(f"Socket connection closed {address}")
        try:
            mi.create(data["date"], data["username"], data["message"])
        except Exception as e:
            print(e)
            sock.close()
            return
        sock.close()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(10)
    print(f"Start echo server {server_socket.getsockname()}")
    with cf.ThreadPoolExecutor(10) as client_pool:
        try:
            while True:
                new_sock, address = server_socket.accept()
                client_pool.submit(handle, new_sock, address)
        except KeyboardInterrupt:
            print(f"Destroy server")
        finally:
            server_socket.close()



if __name__ == "__main__":
    run_server(TCP_IP, TCP_PORT)
