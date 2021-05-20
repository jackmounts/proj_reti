"""
    Elaborato Programmazione di Reti
            a.a. 2020/2021
       Monti Giacomo - matricola:
      Sanità Riccardo - matricola:
              Traccia 2
"""

# !/bin/env python
import cgi
import sys
import signal
import http.server
import socketserver
import threading
import ctypes
from datetime import time

waiting_refresh = threading.Event()

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8080

login_page = """
    <head>
        <meta charset="UTF-8">
        <title>Login</title>
        <style>
            body, html {
                width: 100%;
                height: 100%;
            }

            body, p {
                color: #6b747b;
                font: 400 1rem/1.625rem "Open Sans", sans-serif;
                text-align: center;
            }

            p2 {
                font-size: 3rem;
                text-align: center;
                padding: 10px;
            }

        </style>
    </head>
    <body>
        <br>
        <p2> Login ai Servizi Sanitari DISI </p2>
        <br>
        <br>
        <form action="http://127.0.0.1:{port}/logging" method="post">
            <div class="container">
                <label for="uname"><b>Username</b></label>
                <input type="text" placeholder="Enter Username" name="uname" required>
                <br>
                <label for="psw"><b>Password</b></label>
                <input type="password" placeholder="Enter Password" name="psw" required>
                <br>
                <button type="submit">Login</button>
            </div>
        </form>
        <p> Non sei ancora registrato/a? <a href="register.html">Qui puoi farlo!</a>
    </body>
"""

register_page = """
    <head>
        <meta charset="UTF-8">
        <title>Login</title>
        <style>
            body, html {
                width: 100%;
                height: 100%;
            }

            body, p {
                color: #6b747b;
                font: 400 1rem/1.625rem "Open Sans", sans-serif;
                text-align: center;
            }

            p2 {
                font-size: 3rem;
                text-align: center;
                padding: 10px;
            }

        </style>
    </head>
    <body>
        <br>
        <p2> Iscrizione ai Servizi Sanitari DISI </p2>
        <br>
        <br>
        <form action="http://127.0.0.1:{port}/registering" method="post">
            <div class="container">
                <label for="uname"><b>Username</b></label>
                <input type="text" placeholder="Enter Username" name="uname" required>
                <br>
                <label for="psw"><b>Password</b></label>
                <input type="password" placeholder="Enter Password" name="psw" required>
                <br>
                <button type="submit">Login</button>
            </div>
        </form>
        <p> Sei già registrato/a? <a href="login.html">Fai il login qui!</a>
    </body>
"""


class Authenticator:
    def Register(self, user, password):
        if not Authenticator.Login(self, user, password):
            log = open('.users', 'a')
            log.write('$user:' + user + '$pass:' + password + '\n')
            return True

        return False

    def Login(self, user, password):
        with open('.users', 'r') as file:
            for line in file:
                if line.find(user) > 0 and line.find(password) > 0:
                    return True
        return False


class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/Pages/login.html'

        if self.path == '/Pages/transition.html':
            self.path = '/Pages/login.html'

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            if "login_name" in form and "login_psw" in form:
                if Authenticator.Login(Authenticator,
                                       form.getvalue("login_name"),
                                       form.getvalue("login_psw")):
                    print("User " + form.getvalue("login_name") + " is trying to log in with password: "
                          + form.getvalue("login_psw"))
                    self.path = "../Pages/index.html"
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)
                else:
                    self.path = "../Pages/login.html"
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)

            if "register_name" in form and "register_psw" in form:
                if Authenticator.Register(Authenticator,
                                          form.getvalue("register_name"),
                                          form.getvalue("register_psw")):
                    print("User " + form.getvalue("register_name") + " is trying to register with password: "
                          + form.getvalue("register_psw"))
                    self.path = "../Pages/transition.html"
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)
                else:
                    # i need a popup message to show up holy moly i cant find it
                    # ctypes.windll.user32.MessageBoxW(0, "User already existing", "Try again", 1)
                    self.path = "../Pages/register.html"
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)

        except:
            self.send_error(404, 'Bad request submitted.')
            return


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
