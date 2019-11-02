import cgi
import json
from http.server import BaseHTTPRequestHandler

from Net.DependencyNet import DependencyNet


def StartServer():
    port = 8082
    print('server started')
    from http.server import HTTPServer
    sever = HTTPServer(("", port), PostHandler)
    sever.serve_forever()


class PostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     }
        )
        path = self.path
        if path.startswith('/fetchLicense'):
            status_code, message, content = DependencyNet.fetch_dependency_license2(form)
            self.send_response(status_code)
            self.end_headers()
            response = {}
            response['code'] = status_code
            response['message'] = message
            response['content'] = content
            self.wfile.write(json.dumps(response).encode())


if __name__ == '__main__':
    StartServer()
