from http.server import BaseHTTPRequestHandler, HTTPServer


class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Hello, world!\n")


def main():
    server = HTTPServer(("0.0.0.0", 8080), HelloHandler)
    print("Serving on :8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
