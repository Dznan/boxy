import sys
import socket
import threading
from relay import status


_kill = False
_relay_port = 0
_remote_address = ''
_remote_port = 0


def relay():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', _relay_port))

    incoming_setup = False
    client_port = 0
    client_ip = ''

    while True:
        data, from_addr = sock.recvfrom(1024)

        if _kill:
            sock.close()
            return

        if not incoming_setup:
            client_port = from_addr[1]
            client_ip = from_addr[0]
            incoming_setup = True

        if from_addr[0] == client_ip:
            # forward from client to server
            sock.sendto(data, (_remote_address, _remote_port))
            status.bytes_to_remote += sys.getsizeof(data)
        else:
            # forward from server to client
            sock.sendto(data, (client_ip, client_port))
            status.bytes_from_remote += sys.getsizeof(data)


def start(relay_port, remote_address, remote_port):
    global _relay_port
    global _remote_address
    global _remote_port

    _relay_port = relay_port
    _remote_address = remote_address
    _remote_port = remote_port

    relay_thread = threading.Thread(target=relay)
    relay_thread.start()


def stop():
    global _kill
    _kill = True
    # send anything to the input port to trigger it to read, therefore allowing the thread to close
    quit_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    quit_sock.sendto(b'killing', ('127.0.0.1', _relay_port))
    quit_sock.close()
