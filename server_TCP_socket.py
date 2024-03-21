import socket
from concurrent import futures as cf
import json
from mongo_interface import ChatDB
import logging

chat_db = ChatDB()
SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 5000
BUFFER_SIZE = 1024


def run_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SOCKET_HOST, SOCKET_PORT))
    logging.info(f"Server started on socket://{SOCKET_HOST}:{SOCKET_PORT}")
    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            logging.info(f"Get message from {addr}: {data.decode()}")
        chat_db.create(data)
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        logging.info("Server stopped")
        sock.close()


if __name__ == "__main__":
    run_socket_server()
