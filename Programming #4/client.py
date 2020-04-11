import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8


def checksum(str):
    csum = 0
    countTo = (len(str) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = str[count + 1] * 256 + str[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(str):
        csum = csum + str[len(str) - 1].decode()
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # print(recPacket)

        # Fill in start
        # get header of ICMP reply
        header = recPacket[20: 28]
        # print(struct.unpack("!bbHHh", header))

        icmp_type, icmp_code, checksum, packet_id, sequence = struct.unpack("!bbHHh", header)
        if icmp_type == 0 and icmp_code == 0 and packet_id == ID:
            length = struct.calcsize("!d")
            # print(struct.unpack("!d", recPacket[28: 28+length]))
            timeSent = struct.unpack("!d", recPacket[28: 28 + length])[0]

            ttl = struct.unpack("c", recPacket[8:9])[0]
            # print(ttl)
            # print(type(ttl))
            # print(binascii.hexlify(ttl))
            ttl = int(binascii.hexlify(ttl), 16)
            # print(ttl)
            rtt = timeReceived - timeSent
            return (length, addr, sequence, ttl, rtt)

        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        print(timeLeft)
        if timeLeft <= 0:
            return "Request timed out"


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("!d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))
    # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object


def doOnePing(destAddr, timeout):
    icmp = socket.getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details see: http://sock-raw.org/papers/sock_raw

    # Fill in start
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    # Fill in end

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    ret = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return ret


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client’s ping or the server’s pong is lost
    dest = socket.gethostbyname(host)
    print("Pinging " + dest + " using Python:")

    # Send ping requests to a server separated by approximately one second

    # loss = 0
    for i in range(10):
        ret = doOnePing(dest, timeout)
        if (ret == "Request timed out."):
            print("Request timed out.")
            # loss += 1
        else:
            # get information from ret
            length = ret[0]
            saddr = ret[1][0]
            seq = ret[2]
            ttl = ret[3]
            rtt = int(ret[4] * 1000)
            print('%d bytes from %s: icmp_seq=%d ttl=%d time=%.3fms' % (length, saddr, seq, ttl, rtt))
            # print("Received from " + dest + ": byte(s)=" + str(bytes) + " delay=" + str(delay) + "ms TTL=" + str(ttl))
        time.sleep(1)  # one second
    # print("Packet: sent = " + str(4) + " received = " + str(4-loss) + " lost = " + str(loss))

    return


if len(sys.argv) != 2:
    print("Usage: sudo python client.py hostname")
    sys.exit()
hostname = sys.argv[1]
ping(hostname)
# ping("www.google.com")