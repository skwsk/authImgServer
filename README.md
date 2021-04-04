### Simple HTTP Server good to browse Image files

This is simple HTTP server easy to browse images in directories 
 - Based on list_directory of python3 http.server.SimpleHTTPRequestHandler
 - Support basic authentication

## How to run

Move to the root directory and run like below.

Web server without authentication on default port 8000

'''
/<path>/<of>/<file>/server.py
'''

Web server with basic authentication on specified <port>

'''
/<path>/<of>/<file>/server.py -a <username>:<password> -p <port>
'''

