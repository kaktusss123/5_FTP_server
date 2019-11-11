import os
import socket
from threading import Thread
from json import load, dump

commands = {
    'ls': ls,
    'mkdir': mkdir,
    'rmdir': rmdir,
    'rm': rm,
    'download': download,
    'upload': upload
}


class UserDisconnectedError(Exception):
    pass


def send(conn: socket.socket, msg: str):
    """
    Split message into chunks of 1024 bytes and send them consequently
    """
    msg = msg.strip().replace('  ', ' ')
    header = len(msg)  # No need in extra spaces
    msg_lst = [f'{header:5}{msg[:1019]}']  # First el of list is `{header}{msg}`
    msg = msg[1019:]
    while len(msg) >= 1024:  # Split big message into chunks
        msg_lst.append(msg[:1024])
        msg = msg[1024:]
    for i in msg_lst:  # Send all chunks
        conn.send(i.encode())


def recv(conn: socket.socket):
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


def auth(conn: socket.socket):
    with open('auth_list.json', encoding='utf-8') as f:
        auth_list = load(f)
    send(conn, 'Would you like to sign up? [y]/n')
    sign_up = recv(conn)
    pre_phrase = ''
    if sign_up != 'n':
        while True:
            send(conn, 'Username: ')
            uname = recv(conn)
            if uname in auth_list:
                send(conn, 'User already exists, retry? [y]/n')
                retry = recv(conn)
                if retry != 'n':
                    continue
                else:
                    raise UserDisconnectedError()
            send(conn, 'Password: ')
            passwd = recv(conn)
            send(conn, 'Repeat your password: ')
            rpasswd = recv(conn)
            if passwd == rpasswd:
                pre_phrase = 'Register successful! '
                auth_list[uname] = passwd
                with open('auth_list.json', 'w', encoding='utf-8') as f:
                    dump(auth_list, f)
                break

    while True:
        send(conn, pre_phrase + 'Username: ')
        uname = recv(conn)
        send(conn, 'Password: ')
        passwd = recv(conn)
        if auth_list.get(uname) == passwd:
            send(conn, f'Success! Greetings, {uname}!')
            return uname
        pre_phrase = 'Try again! '


def handle_client(conn, addr):
    try:
        uname = auth(conn)
        # Check for existing user dir
        for _, dirs, _ in os.walk('.'):
            if uname == dirs:
                break
        else:
            os.mkdir(uname)
        # Setting dir to user dir
        os.chdir(uname)

        while 1:
            comm = recv(conn)
            if comm == 'exit':
                raise UserDisconnectedError()

    except UserDisconnectedError:
        conn.close()
        return


if __name__ == "__main__":
    # Start server and bind to addr
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = input('Host: ') or 'localhost'
    port = 0
    try:
        port = int(input('Port: '))
    except:
        pass
    finally:
        sock.bind((host, port))
        print(f'Server binded to {sock.getsockname()}')

    # Mainloop
    sock.listen(10)
    while not False:
        conn, addr = sock.accept()
        Thread(target=handle_client, args=(conn, addr)).start()
