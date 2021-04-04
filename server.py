#!/usr/bin/python

# Reference:
#  https://github.com/python/cpython/blob/3.8/Lib/http/server.py
#  https://docs.python.org/3.8/library/socketserver.html

import http.server
import html
import io
import os
import socketserver
import sys
import urllib.parse
import argparse
from http import HTTPStatus

parser = argparse.ArgumentParser()
parser.add_argument('-a','--auth',help='<username>:<password>')
parser.add_argument('-p','--port',help='port number (Default:8000)')
args = parser.parse_args()
key = ''
if args.auth:
    import base64
    key = args.auth.encode("utf-8")
port = 8000
if args.port and int(args.port) > 0:
    port = int(args.port)

class customHandler(http.server.SimpleHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header('WWW-Authenticate', 'Basic realm="WebSite"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global key
        if key == '':
            """Serve a GET request."""
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()
        else:
            b64key = base64.b64encode(bytes(key))
            authorization = self.headers.get("authorization")
            if authorization == 'Basic '+b64key.decode("utf-8"):
                http.server.SimpleHTTPRequestHandler.do_GET(self)
            else:
                self.do_AUTHHEAD()

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        ##############################################
        #r.append('<title>%s</title>\n</head>' % title)
        #r.append('<body>\n<h1>%s</h1>' % title)
        #r.append('<hr>\n<ul>')
        r.append('<title>%s</title>\n' % title)
        r.append('<style>\nimg{ max-width: 100%; max-height: 90vh; }\n</style>\n')
        r.append('</head>')
        r.append('<body>\n')
        l = []
        i = []

        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            '''
            r.append('<li><a href="%s">%s</a></li>'
                    % (urllib.parse.quote(linkname,
                                          errors='surrogatepass'),
                       html.escape(displayname, quote=False)))
            '''
            if os.path.isfile(fullname) and os.path.splitext(name.lower())[1] in ['.png','.gif','.jpeg','.jpg']:
                i.append('<div><img src="%s"></img></div>\n' % name)
            else:
                l.append('<li><a href="%s">%s</a></li>'
                        % (urllib.parse.quote(linkname,
                            errors='surrogatepass'),
                            html.escape(displayname, quote=False)))
        if len(l)>0:
            r.append('<ul>')
            r.extend(l)
            r.append('</ul>\n<hr>\n')
        if len(i)>0:
            r.extend(i)
        r.append('</body>\n</html>\n')
        #r.append('</ul>\n<hr>\n</body>\n</html>\n')
        ##############################################
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

if __name__=='__main__':
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", port), customHandler)
    if key:
        print(f"Serving on 0.0.0.0:{port} with authentication...")
    else:
        print(f"Serving on 0.0.0.0:{port} without authentication...")
    httpd.serve_forever()
