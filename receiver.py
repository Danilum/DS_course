import socket
import os.path
from threading import Thread

clients = []


class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    def _clear_echo(self, data):
        self.sock.sendall('\033[F\033[K'.encode())
        data = 'me> '.encode() + data
        self.sock.sendall(data)

    def _broadcast(self, data):
        data = (self.name + '> ').encode() + data
        for u in clients:
            if u == self.sock:
                continue
            u.sendall(data)

    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        filename = self.sock.recv(1024).decode()
        if os.path.isfile(filename):
            i = 1
            while True:
                index = filename.rindex('.')
                copy = filename[:index] + '_copy' + str(i) + filename[index:]
                if os.path.isfile(copy):
                    i += 1
                else:
                    filename = copy
                    break
        f = open(filename, 'wb')
        self.sock.send('File created'.encode())
        while True:
            data = self.sock.recv(1024)
            if data:
                f.write(data)
            else:
                self._close()
                return


def main():
    next_name = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 8800))
    sock.listen()
    while True:
        con, addr = sock.accept()
        clients.append(con)
        name = 'user' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()