import mimetypes
import json
import mongo_interface as mi
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote_plus
from client_TCP_socket import send_message
from jinja2 import Environment, FileSystemLoader
from datetime import datetime


BASE_DIR = Path(__file__).parent
jinja = Environment(loader=FileSystemLoader(BASE_DIR.joinpath("templates")))


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = self.headers.get("Content-Length")
        data = self.rfile.read(int(size)).decode()
        data_parse = unquote_plus(data)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        data_dict["date"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(data_dict)
        send_message("127.0.0.1", 8080, json.dumps(data_dict))
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        router = urlparse(self.path).path
        match router:
            case "/":
                self.send_html("index.html")
            case "/message":
                self.send_html("message.html")
            case "/blog":
                self.render_template("blog.jinja")
            case _:
                file = BASE_DIR.joinpath(router[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("error.html", 404)

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

        content = mi.read()

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


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run_http_server()
