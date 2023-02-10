#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Junhyeon Cho
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
import json

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):
    
    redirect_codes = [301, 302, 307, 308]

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None
    
    def connect_url(self, url):
        if 'http' != url.lower()[0:7]:
            url = 'http://' + url
        
        uo = urllib.parse.urlparse(url)
        host = uo.hostname
        port = uo.port
        path = uo.path
        
        if not port:
            port = 80
            
        if not path:
            path = '/'
        
        self.connect(host, port)
        
        return host, path
        
    
    def get_response(self):
        data = self.recvall(self.socket)
        self.close()
        print(data)
        
        return self.parse_data(data)
        

    def parse_data(self,data):
        header, body = data.split('\r\n\r\n')
        i = data.index(' ')
        return data[i+1:i+4], header, body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def make_request(self, lines):
        return "\r\n".join(lines)

    def GET(self, url, args=None):
        host, path = self.connect_url(url)

        request = self.make_request([
            f'GET {path} HTTP/1.1', 
            'Host: ' + host, 
            'User-Agent: Mozilla/5.0',
            'Accept: */*',
            'Connection: close',
            '\r\n'
        ])
        self.sendall(request)
        
        code, header, body = self.get_response()
        if code in self.redirect_codes:
            pass
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, path = self.connect_url(url)
        content = urllib.parse.urlencode(args) if args else ''

        request = self.make_request([
            f'POST {path} HTTP/1.1', 
            'Host: ' + host, 
            'User-Agent: Mozilla/5.0',
            'Accept: */*',
            'Content-Type: application/x-www-form-urlencoded',
            'Content-Length: ' + str(len(content)),
            '\r\n' + content
        ])
        self.sendall(request)
        
        code, header, body = self.get_response()
        if code in self.redirect_codes:
            print(f'!!!!!\n{json.loads(header)}')
            
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        return self.POST( url, args ) if (command == "POST") else self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
