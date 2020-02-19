from socket import *
from time import time, ctime  # retrieve time
import sys

# arguments check
if (len(sys.argv) != 3):
    print("Wrong input of arguments! Please use: ")
    print("StandardUDPPingerClient.py server_host server_port")
    sys.exit()

# Preparing the socket
server_host, server_port = sys.argv[1:]
clientSocket = socket(AF_INET, SOCK_DGRAM)  # use UDP
clientSocket.settimeout(1)  # set receive timeout to 1 second

rtt_records = []

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
        rtt_records.append(RTT)
        msg_back = msg_back.decode()
        print("response message from server: " + msg_back)
        print("RTT: %.6fs\n" % RTT)
    except:
        print("Request timed out\n")

print(rtt_records)
print("Maximum RTT: %.6fs" % max(rtt_records))
print("Minimum RTT: %.6fs" % min(rtt_records))
print("Average RTT: %.6fs" % (sum(rtt_records) / len(rtt_records)))
print("Package loss rate: %i%%" % ((10 - len(rtt_records)) * 10))

clientSocket.close()