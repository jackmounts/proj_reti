import cgi

form = cgi.FieldStorage()
name = form.getvalue('uname')
psw = form.getvalue('psw')
