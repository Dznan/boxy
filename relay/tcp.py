import sys
import socket
import threading
from relay import status

_kill = False
_relay_port = 0
_remote_address = ''
_remote_port = 0

_clients = 0
_servers = 0

_socks = []


def accept_clients():
    global _socks

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.bind(('0.0.0.0', _relay_port))
    client_sock.listen(10)

    while True:
        client_conn, addr = client_sock.accept()

        if _kill:
            client_sock.close()
            for sock in _socks:
                sock.close()
            return

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.connect((_remote_address, _remote_port))

        _socks.append(client_conn)
        _socks.append(server_sock)

        client_thread = threading.Thread(target=client_worker, kwargs={'client': client_conn, 'server': server_sock})
        client_thread.start()

        server_thread = threading.Thread(target=server_worker, kwargs={'client': client_conn, 'server': server_sock})
        server_thread.start()


def close(client, server):
    try:
        client.close()
    except socket.error:
        pass

    try:
        server.close()
    except socket.error:
        pass


def client_worker(client, server):
    global _clients
    _clients += 1
    while True:
        try:
            data = client.recv(1)

            if data == '':
                close(client, server)
                break

            server.sendall(data)
            status.bytes_to_remote += sys.getsizeof(data)
        except socket.error:
            close(client, server)
            break
    _clients -= 1


def server_worker(client, server):
    global _servers
    _servers += 1
    while True:
        try:
            data = server.recv(1)

            if data == '':
                close(client, server)
                break

            client.sendall(data)
            status.bytes_from_remote += sys.getsizeof(data)
        except socket.error:
            close(client, server)
            break
    _servers -= 1


def start(relay_port, remote_address, remote_port):
    global _relay_port
    global _remote_address
    global _remote_port

    _relay_port = relay_port
    _remote_address = remote_address
    _remote_port = remote_port

    accept_thread = threading.Thread(target=accept_clients)
    accept_thread.start()


def stop():
    global _kill
    _kill = True
    # connect to the input port therefore allowing the thread to close
    quit_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    quit_sock.connect(('127.0.0.1', _relay_port))
    quit_sock.close()
