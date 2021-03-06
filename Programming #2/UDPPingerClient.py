from socket import *
from time import time, ctime  # retrieve time
import sys

# arguments check
if (len(sys.argv) != 3):
    print("Wrong input of arguments! Please use: ")
    print("UDPPingClient.py server_host server_port")
    sys.exit()

# Preparing the socket
server_host, server_port = sys.argv[1:]
clientSocket = socket(AF_INET, SOCK_DGRAM)  # use UDP
clientSocket.settimeout(1)  # set receive timeout to 1 second

# send 10 pings to the server
for i in range(1, 11):
    begin_time = time()  # record the beginning time
    # print(begin_time)
    message = "Ping " + str(i) + " " + ctime(begin_time)

    try:
        clientSocket.sendto(message.encode(), (server_host, int(server_port)))
        msg_back, server_address= clientSocket.recvfrom(1024)

        # Checking the current time and if the server answered
        end_time= time()
        # print(end_time)
        RTT = end_time - begin_time
        msg_back = msg_back.decode()
        print("response message from server: " + msg_back)
        print("RTT: %.6fs\n" % RTT)
    except:
        print("Request timed out\n")

clientSocket.close()
