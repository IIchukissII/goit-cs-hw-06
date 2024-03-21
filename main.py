import mimetypes
import json
import socket
import logging
from urllib.parse import urlparse, unquote_plus
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from mongo_interface import ChatDB

from datetime import datetime

from jinja2 import Environment, FileSystemLoader

URI = "mongodb://goit-cs-hw-06-mongodb-1:27017"
BASE_DIR = Path(__file__).parent
BUFFER_SIZE = 1024
HTTP_PORT = 3000
HTTP_HOST = '0.0.0.0'
SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 5000
jinja = Environment(loader=FileSystemLoader(BASE_DIR.joinpath("templates")))
chat_db = ChatDB()


class CatFramework(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.send_html("index.html")
        elif path == "/message":
            self.send_html("message.html")
        elif path == "/blog":
            self.render_template("blog.jinja")
        else:
            file_path = BASE_DIR.joinpath(path[1:])
            if file_path.exists():
                self.send_static(file_path)
            else:
                self.send_html("error.html", 404)

    def do_POST(self):
        size = self.headers.get("Content-Length")
        data = self.rfile.read(int(size)).decode()
        data_parse = unquote_plus(data)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        data_dict["date"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(json.dumps(data_dict).encode(), (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        # print(unquote_plus(data))

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as f:
            self.wfile.write(f.read())

    def render_template(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        content = chat_db.read_all()

        template = jinja.get_template(filename)
        html = template.render(content=content, title="Blog").encode()
        self.wfile.write(html)

    def send_static(self, filename, status=200):
        self.send_response(status)
        mimetype = mimetypes.guess_type(filename)[0] if mimetypes.guess_type(filename)[0] else "text/plain"
        self.send_header("Content-type", mimetype)
        self.end_headers()
        with open(filename, "rb") as f:
            self.wfile.write(f.read())


def save_data(data):
    parse_data = unquote_plus(data.decode())
    try:
        parse_data = json.loads(parse_data)
        chat_db.create(parse_data)
    except ValueError as e:
        logging.error(f"Parse error: {e}")
    except Exception as e:
        logging.error(f"Failed to save: {e}")


def run_http_server():
    httpd = HTTPServer((HTTP_HOST, HTTP_PORT), CatFramework)
    try:
        logging.info(f"Server started on http://{HTTP_HOST}:{HTTP_PORT}")
        httpd.serve_forever()
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        logging.info("Server stopped")
        httpd.server_close()


def run_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SOCKET_HOST, SOCKET_PORT))
    logging.info(f"Server started on socket://{SOCKET_HOST}:{SOCKET_PORT}")
    try:
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            logging.info(f"Get message from {addr}: {data.decode()}")
            save_data(data)
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        logging.info("Server stopped")
        sock.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(threadName)s - %(message)s")
    http_thread = Thread(target=run_http_server, name="http_server")
    http_thread.start()

    socket_thread = Thread(target=run_socket_server, name="socket_server")
    socket_thread.start()
