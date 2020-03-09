import argparse
# coding:utf-8
from socket import *
import sys
import time
import os

# arguments check
parser = argparse.ArgumentParser()
parser.add_argument('-x', dest='ttl')
parser.add_argument('host', type=str)
parser.add_argument('port', type=int)
args = parser.parse_args()
if args.ttl:
    ttl = args.ttl

# if (len(sys.argv) != 3):
#     print("Wrong input of arguments! Please use: ")
#     print("server.py server_host server_port")
#     sys.exit()

# Preparing the socket
server_host = args.host
server_port = args.port
proxy_server_socket = socket(AF_INET, SOCK_STREAM)
# proxy_server_socket.bind(('10.0.0.102', 9999))
proxy_server_socket.bind((server_host, server_port))
proxy_server_socket.listen(5)
cache_time = {}

while True:
    print('The proxy server is waiting for requests . . .')
    client_socket, addr = proxy_server_socket.accept()
    print('Connected to client host: ', addr)
    msg_from_client = client_socket.recv(2048).decode()
    cli_get_request = msg_from_client.split()[1]

    # parse message
    # get filename and remote host
    # handle requests containing "http://" prefix
    if "//" in cli_get_request:
        file_name = cli_get_request.partition("//")[2]
    # handle requests without "http://" prefix, such as www.google.com
    else:
        file_name = cli_get_request.split('/', 1)[1]

    remote_host = file_name.split("/")[0]

    # store the original file url, which is used for requesting resources in remote host
    # note that the original file url does not contain the remote host address
    if '/' in file_name:
        origin_file_url = file_name.split('/', 1)[1]
    else:
        origin_file_url = ''

    print("Get filename: " + file_name)
    print("Remote host: " + remote_host)
    file_exist = False

    # if cache exists and time passed exceeds ttl, remove cache and pop from dictionary
    local_file_name = file_name.replace('/', '_') + '.cache'
    if local_file_name in cache_time.keys() and args.ttl:
        diff = (time.time() - cache_time[local_file_name]) * 1000
        if diff > float(ttl) and os.path.exists("./" + local_file_name):
            os.remove("./" + local_file_name)
            cache_time.pop(local_file_name)

    try:
        f = open(local_file_name, "br")
        data_to_client = f.read()
        file_exist = True
        print('Return cache file to client . . .\n')
        client_socket.send(data_to_client)

    except IOError:
        print('cache file exist: ', file_exist)
        if not file_exist:
            print('Proxy server creating new socket to connect remote host . . .')
            proxy_to_remote_socket = socket(AF_INET, SOCK_STREAM)

            try:
                proxy_to_remote_socket.connect((remote_host, 80))
                print('New socket successfully connected to the remote host with port 80 . . .')

                get_request = 'GET /' + origin_file_url + ' HTTP/1.0\r\n\r\n'
                print("Get request: " + get_request)
                proxy_to_remote_socket.send(get_request.encode())

                cache_file = open("./" + local_file_name, "wb")
                cache_data = "".encode()

                # repeatedly receive data from remote host
                print("proxy server fetching data from remote host and sending to client. . .")
                while True:
                    remote_data = proxy_to_remote_socket.recv(2048)
                    client_socket.sendall(remote_data)
                    cache_data += remote_data
                    if (len(remote_data) == 0):
                        break

                print("proxy server caching remote data . . .")
                cache_file.write(cache_data)
                cache_file.close()
                # store the begin time of each cache file
                if local_file_name not in cache_time.keys():
                    cache_time[local_file_name] = time.time()

            except:
                print("Connection failure with illegel request!\n")
        else:
            print('404 File Not Found!')


    client_socket.close()
proxy_server_socket.close()