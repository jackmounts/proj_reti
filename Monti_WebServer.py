#!/bin/env python
import sys
import signal
import http.server
import socketserver
import threading
from flask import Flask, render_template

app = Flask(__name__)

# Manage the wait without busy waiting
waiting_refresh = threading.Event()

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8080


@app.route('/')
def index():
    return render_template('login.html')


class Authenticator:
    @app.route('/Register/')
    def Register(self, user, password):
        if not Authenticator.Login(self, user, password):
            log = open('.users', 'a')
            log.write('$user:' + user + '$pass:' + password)
            return True

        return False

    @app.route('/Login/')
    def Login(self, user, password):
        with open('.users', 'r') as file:
            for line in file:
                if line.find(user) > 0 and line.find(password) > 0:
                    return True

        return False


class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/Pages/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


server = socketserver.ThreadingTCPServer(('127.0.0.1', port), ServerHandler)
print('Server is up and running on port:', port)


def signal_handler(signal, frame):
    print('Exiting http server')
    try:
        if server:
            server.server_close()
    finally:
        waiting_refresh.set()
        sys.exit(0)


def main():
    server.daemon_threads = True
    server.allow_reuse_address = True
    signal.signal(signal.SIGINT, signal_handler)
    # Loop
    try:
        while True:
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
    app.run()
