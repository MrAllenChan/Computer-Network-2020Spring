# Import socket module
from socket import *
import sys

# arguments check
if (len(sys.argv) != 4):
    print("Wrong input of arguments, please use:")
    print("WebClient.py server_host server_port filename")
    sys.exit()

# Preparing the socket
server_host, server_port, filename = sys.argv[1:]
clientSocket = socket(AF_INET, SOCK_STREAM)

# try to establish TCP connection
try:
    clientSocket.connect((server_host, int(server_port)))
except:
    print("Sorry, the server is currently unavailable")
    clientSocket.close()
    sys.exit()

print("Connection established.")

# Send the HTTP request
http_request = "GET /" + filename + " HTTP/1.1\r\n\r\n"
clientSocket.send(http_request.encode())
print("Request message sent.")

# Receive the response
print("Server HTTP Response:\r\n")

# Repeatly receive data until there is no new data arriving
# ensure that we will receive the entire message, if its size exceeds the buffer
data = ""
while True:
    clientSocket.settimeout(5)
    newData = clientSocket.recv(2048).decode()
    data += newData
    if (len(newData) == 0):
        break
print(data)

# Close client socket
print("Closing client socket . . .")
clientSocket.close()