import threading
import sys
import os
from socket import *



def client_dedicated_socket(connectionSocket, clientAddress):
    try:
        message = connectionSocket.recv(2048).decode()
        
        if not message:
            return
        
        # Message e da forma: ['GET', '/index.html', 'HTTP/1.1', ...]
        fields = message.split()
        if fields[0] == "GET": # a aplicacao so aceita requisicoes GET
            file = fields[1]
            file = file[1:] #remove a '/' inicial
            
            # Devolve o index.html para requisicao GET / ou GET /index.html
            if file == "": file = "index.html"
            
            # Monta o nome relativo do arquivo
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(BASE_DIR, file)
            
            # Arquivo txt deve ser devolvido como text/plain para o download funcionar
            if file.endswith(".txt"):
                file_type = "text/plain; charset=utf-8"
            else:
                file_type = "text/html; charset=utf-8"
                
            with open(filepath, "r", encoding="utf-8") as f:
                outdata = f.read()
            
            #monta o header HTTP da mensagem
            header = f"HTTP/1.1 200 OK\r\nContent-Type: {file_type}\r\n\r\n"
            connectionSocket.sendall((header + outdata).encode("utf-8"))
        
            
    except IOError:
        #Header de erro 404
        header404 = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
        
        #Carrega o conteudo da pagina para erros 404
        with open(os.path.join(BASE_DIR, "404.html"), "r", encoding="utf-8") as f:
            message404 = f.read()
        connectionSocket.sendall((header404 + message404).encode())
    
    finally:
        connectionSocket.close()
        

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM) #socket TCP para o servidor
serverSocket.bind(('', serverPort))
serverSocket.listen(10)
while True:
    # Aceita conexao do cliente atual, criando socket dedicada para tratar a requisicao
    connectionSocket, addr = serverSocket.accept()
    
    # Uso de thread para concorrencia
    client_thread = threading.Thread(target=client_dedicated_socket, 
                                        args=(connectionSocket, addr))
    client_thread.start()
        