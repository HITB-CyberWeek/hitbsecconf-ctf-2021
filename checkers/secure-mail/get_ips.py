#!/usr/bin/env python3

import ifaddr
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import urlparse, unquote

PORT=8090
files = set()

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    def do_GET(self):
        if self.path == '/':
            self.send_error(403, 'Forbidden')
        elif self.path == '/ips':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            ips = [a.ips[0].ip for a in ifaddr.get_adapters() if a.nice_name.startswith('tun')]
            self.wfile.write(json.dumps(ips).encode())
        elif self.path.startswith('/check'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            file = urlparse(self.path).query.split('=')[1]
            self.wfile.write(json.dumps([file in files]).encode())
        else:
            file = self.path[1:]
            if os.path.isfile(file):
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(file, 'rb') as f: 
                    self.wfile.write(f.read())
                files.add(file)
            else:
                self.send_error(404, 'Not found')
        return

def run(server_class=HTTPServer, handler_class=Server, port=PORT):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    
if __name__ == "__main__":
    run()
