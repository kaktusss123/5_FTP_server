from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


class UserDisconnectedError(Exception):
    pass


def send(conn: socket, msg: str):
    """
    Split message into chunks of 1024 bytes and send them consequently
    """
    header = len(msg.strip().replace('  ', ' '))  # No need in extra spaces
    msg_lst = [f'{header:5}{msg[:1019]}']  # First el of list is `{header}{msg}`
    msg = msg[1019:]
    while len(msg) >= 1024:  # Split big message into chunks
        msg_lst.append(msg[:1024])
        msg = msg[1024:]
    for i in msg_lst:  # Send all chunks
        conn.send(i.encode())


def recv(conn: socket):
    """
    Receive multiple messages and join them
    """
    header = conn.recv(5)
    try:
        header = int(header.decode())
    except ValueError:
        print('Connection aborted')
        raise UserDisconnectedError()
    msg_lst = [conn.recv(1019).decode() if header >= 1019 else conn.recv(header).decode()]
    header -= 1019
    while header >= 1024:
        msg_lst.append(conn.recv(1024).decode())
        header -= 1024
    if header > 0:
        msg_lst.append(conn.recv(header).decode())
    return ''.join(msg_lst)


if __name__ == "__main__":
    sock = socket(AF_INET, SOCK_STREAM)
    host = input('Host: ') or 'localhost'
    port = input('Port: ')
    while not port.strip().isdigit():
        port = input('Port: ')
    try:
        sock.connect((host, int(port)))
        while not False:
            msg = recv(sock)
            print(f'[server] {msg}')
            comm = input('[input] ')
            send(sock, comm)
    finally:
        sock.close()
