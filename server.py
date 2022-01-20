#  coding: utf-8 
from asyncio import format_helpers
from email.mime import base
import socketserver
from pathlib import Path
from urllib import request

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Modifications copyright 2021 Joshua Patrick
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of:\n", self.data.decode('utf-8'))

        data_split = self.data.decode('utf-8').split()
        if len(data_split) < 2:
            # Return 400 Bad Request
            self.request.sendall(bytearray("HTTP/1.1 400 Bad Request\r\n\r\n",'utf-8'))
            return
        req_type = self.data.decode('utf-8').split()[0]
        resource = self.data.decode('utf-8').split()[1]

        if req_type != "GET":
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n",'utf-8'))
            return
        
        print ("Recieved request for resource {}".format(resource))
        
        # Check for sneaky hackers i.e. '..'
        if ".." in resource:
            self.request.sendall(bytearray("HTTP/1.1 404 Not FOUND!\r\n\r\n",'utf-8'))
            return


        local_resource = "./www" + resource

        # add index.html to directories
        if Path(local_resource).is_dir():
            # Fix bad directory names with 301
            if resource[-1] != "/":
                self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:8080{}/\r\n\r\n".format(resource),'utf-8'))
                return
            local_resource = local_resource + "index.html"

        # check if file exists before attempting to open
        if Path(local_resource).is_file():
            m_file = open(local_resource, "r")
            mime_type = ""
            if local_resource[-5:] == ".html":
                mime_type = "html"
            if local_resource[-4:] == ".css":
                mime_type = "css"
            default_str = "HTTP/1.1 200 OK\r\nContent-Type: text/{}\r\n\r\n".format(mime_type)
            http_response = default_str + m_file.read()
            print("\nSending response to client:\n", http_response)
            self.request.sendall(bytearray(http_response,'utf-8'))
        else:
            # Bad resource request 404 not found
            self.request.sendall(bytearray("HTTP/1.1 404 Not FOUND!\r\n\r\n",'utf-8'))
        print ()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
