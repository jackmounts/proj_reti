"""
    Elaborato Programmazione di Reti
            a.a. 2020/2021
  Monti Giacomo - matricola: 0000922997
 Sanità Riccardo - matricola: 0000915154
              Traccia 2
"""

# !/bin/env python
import cgi
import sys
import signal
import http.server
import socketserver
import threading

waiting_refresh = threading.Event()

# Sets server' port as argument passed via terminal or sets it to 8080 by default
if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8080

# Useful html for the login page
login_header = """
<!DOCTYPE html>
<html lang="it">
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
        <form method="post">
                <label for="login_name"><b>Username</b></label>
                <input type="text" placeholder="Enter Username" id="login_name" name="login_name" required> <br>
                <label for="login_psw"><b>Password</b></label>
                <input type="password" placeholder="Enter Password" id="login_psw" name="login_psw" required> <br>
                <input type="submit" value="Login">
        </form>
        <p> Non sei ancora registrato/a? <a href="../Pages/register.html">Registrati qui!</a>
    </body>
"""

# Warning for login page
login_warning = """
<p style="color: red">L'utente non esiste, riprova o registrati</p>
"""

# Useful html for the register page
register_header = """
<!DOCTYPE html>
<html lang="it">
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
        <form method="post">
            <div class="container">
                <label for="register_name"><b>Username</b></label>
                <input type="text" placeholder="Enter Username" id="register_name" name="register_name" required> <br>
                <label for="register_psw"><b>Password</b></label>
                <input type="password" placeholder="Enter Password" id="register_psw" name="register_psw" required> <br>
                <input type="submit" value="Register">
            </div>
        </form>
        <p> Sei già registrato/a? <a href="../Pages/login.html">Fai il login qui!</a>
"""

# Warning for register page
register_warning = """
<p style="color: red">L'utente esiste già, prova a fare il Login!</p>
"""

# transition page header
transition_before_ip = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Redirecting</title>
</head>
<body>
  <p>Registration was successful. Redirecting....</p>
  <script type="text/javascript">
      function sleep(ms) {
        return new Promise(function(res,rej) {
            setTimeout(function(){res()}, ms);
        })
}
      async function change() {
          await(sleep(1000));
          window.location.replace("http://
"""

# Transition page after ip
transition_after_ip = """/Pages/login.html");
      }

      change();
  </script>
"""

# Useful for pages ends
page_end = """
    </body>
</html>
"""


# Simplest user authenticator that saves and reads users and passwords from the .users file
# Does not implement any data encryption. The project is not intended to be used on public
# networks or as base of future projects so it shouldn't matter.
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


# simple.http server handler
class ServerHandler(http.server.SimpleHTTPRequestHandler):
    # Handles GET requests, usually from loading or changing pages
    def do_GET(self):
        # Sets initial path to login
        if self.path == '/':
            self.path = '/Pages/login.html'

        # Sets path from transition to login
        if self.path == '/Pages/transition.html':
            self.path = '/Pages/login.html'

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    # Handles POST requests
    # As of now only login and register form might send POST requests and only these are
    # implemented cases. Others will return a 404 error on catch
    def do_POST(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            # Looks if the POST request is coming from the login form and let the user login if credentials are
            # correct. if correct, the user will be redirected to the index page.
            # If not reloads the page with a warning
            if "login_name" in form and "login_psw" in form:
                if Authenticator.Login(Authenticator,
                                       form.getvalue("login_name"),
                                       form.getvalue("login_psw")):
                    print("User " + form.getvalue("login_name") + " is trying to log in with password: "
                          + form.getvalue("login_psw"))
                    self.path = "../Pages/index.html"
                    create_login_no_warning()
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)
                else:
                    create_login_with_warning()
                    create_register_no_warning()
                    self.path = "../Pages/login.html"
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)

            # Looks if the POST request is coming from the register form and let the user login if credentials are
            # correct. If correct, redirects the user to the login page using a simple "hard coded" transition.
            # If not reloads the page with a warning
            if "register_name" in form and "register_psw" in form:
                if Authenticator.Register(Authenticator,
                                          form.getvalue("register_name"),
                                          form.getvalue("register_psw")):
                    print("User " + form.getvalue("register_name") + " is trying to register with password: "
                          + form.getvalue("register_psw"))
                    create_transition_page()
                    self.path = "../Pages/transition.html"
                    create_register_no_warning()
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)
                else:
                    create_register_with_warning()
                    create_login_no_warning()
                    self.path = "../Pages/register.html"
                    return http.server.SimpleHTTPRequestHandler.do_GET(self)

        except:
            # On bad requests sends a 404 error
            self.send_error(404, 'Bad request submitted.')
            return


# Starting the threaded TCP server on port 127.0.0.1 for localhost access and sets the port selected via terminal
# (or defaulted to 8080)
# Should you want to change from localhost access to a network based local server change the ip variable
# to your device ip
ip = "127.0.0.1"
server = socketserver.ThreadingTCPServer((ip, port), ServerHandler)
print("Server is up and running at " + ip + ":" + str(port))
full_address = ip + ":" + str(port)


# Creates a login.html page without warning
def create_login_no_warning():
    f = open('Pages/login.html', 'w', encoding="utf-8")
    f.write(login_header + "<br>" + page_end)
    f.close()


# Creates a login.html page with a warning
def create_login_with_warning():
    f = open('Pages/login.html', 'w', encoding="utf-8")
    f.write(login_header + "<br>" + login_warning + "<br>" + page_end)
    f.close()


# Creates a register.html page without warning
def create_register_no_warning():
    f = open('Pages/register.html', 'w', encoding="utf-8")
    f.write(register_header + "<br>" + page_end)
    f.close()


# Creates a register.html page with a warning
def create_register_with_warning():
    f = open('Pages/register.html', 'w', encoding="utf-8")
    f.write(register_header + "<br>" + register_warning + "<br>" + page_end)
    f.close()


# Creates a simple transition page that redirects to login.html
def create_transition_page():
    f = open('Pages/transition.html', 'w', encoding="utf-8")
    f.write(transition_before_ip.rstrip() + str(full_address).strip() + transition_after_ip.rstrip() + "<br>" + page_end)


# Closes server on running termination or on ctrl+c
def signal_handler(sig, form):
    print('Exiting http server')
    try:
        if server or sig is signal.SIGINT:
            server.server_close()
    finally:
        waiting_refresh.set()
        sys.exit(0)


# Main loop and page creation on server start
def main():
    server.daemon_threads = True
    server.allow_reuse_address = True
    signal.signal(signal.SIGINT, signal_handler)
    create_login_no_warning()
    create_register_no_warning()
    # Loop
    try:
        while True:
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


# Run method def
if __name__ == "__main__":
    main()
