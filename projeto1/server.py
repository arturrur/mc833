import threading
import sys
import os
from socket import *



def client_dedicated_socket(connectionSocket, clientAddress):
    try:
        message = connectionSocket.recv(2048).decode()
        
        if not message:
            return
        
        # Message é da forma: ['GET', '/index.html', 'HTTP/1.1', ...]
        fields = message.split()
        print(fields)
        if fields[0] == "GET":
            file = fields[1]
            file = file[1:]
            
            if file == "": file = "index.html"
            
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(BASE_DIR, file)
            
            # Arquivo txt deve ser devolvido como text/plain
            if file.endswith(".txt"):
                file_type = "text/plain; charset=utf-8"
            else:
                file_type = "text/html; charset=utf-8"
                
            with open(filepath, "r", encoding="utf-8") as f:
                outdata = f.read()
            
            header = f"HTTP/1.1 200 OK\r\nContent-Type: {file_type}\r\n\r\n"
            connectionSocket.sendall((header + outdata).encode("utf-8"))
        
            
    except IOError:
        header404 = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
        with open(os.path.join(BASE_DIR, "404.html"), "r", encoding="utf-8") as f:
            message404 = f.read()
        connectionSocket.sendall((header404 + message404).encode())
    
    finally:
        connectionSocket.close()
        

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(10)
while True:
    # Connection
    connectionSocket, addr = serverSocket.accept()
    
    # Dedicated socket for every request
    client_thread = threading.Thread(target=client_dedicated_socket, 
                                        args=(connectionSocket, addr))
    
    client_thread.start()
        