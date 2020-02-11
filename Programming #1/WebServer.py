# import socket module
from socket import *

serverSocket = socket(AF_INET, SOCK_STREAM)
# Prepare a sever socket
# Fill in start
hostIP = ''
port = 9999
address = (hostIP, port)
serverSocket.bind(address)
serverSocket.listen(5)
# Fill in end

while True:
    # Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept() # Fill in start  # Fill in end
    print(addr)

    try:
        message = connectionSocket.recv(2048) # Fill in start  # Fill in end
        if not message:
            connectionSocket.close()
            continue

        filename = message.split()[1]
        f = open(filename[1:], 'r')
        outputdata = f.read() # Fill in start  #Fill in end

        # Send one HTTP header line into socket informing that the file has been found
        headerLine = "HTTP/1.1 200 OK\r\n"
        connectionSocket.send(headerLine.encode())
        connectionSocket.send("\r\n".encode())

        # Send the content of the requested file to the client
        # for i in range(0, len(outputdata)):
        #     connectionSocket.send(outputdata[i].encode())
        # connectionSocket.send("\r\n".encode())
        connectionSocket.send(outputdata.encode()) # either way is feasible

        print("Successfully sent file.")
        connectionSocket.close()

    except IOError:
        # Send response message for file not found
        print('Returns the error header to the browser')
        errHeader = "HTTP/1.1 404 Not Found\r\n"
        connectionSocket.send(errHeader.encode())
        connectionSocket.send("\r\n".encode())

        # Open the error page and send to the client
        file = open("notfound.html", 'r')
        outputdata = file.read()

        # for i in range(0, len(outputdata)):
        #     connectionSocket.send(outputdata[i].encode())
        # connectionSocket.send("\r\n".encode())
        connectionSocket.send(outputdata.encode())

        # close client socket
        print("Sent error msg.")
        connectionSocket.close()

serverSocket.close()