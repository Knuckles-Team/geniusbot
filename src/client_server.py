import socket
import threading

# https://techwithtim.net/tutorials/socket-programming/
HEADER = 64
PORT = 5067
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.57.1"  # For Internet Connection Look Up IP Address.
#SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Server:
    server = None
    conn = None
    addr = None

    def __init__(self, address=ADDR):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(address)
        print("[STARTING] server is starting...")
        self.server.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            self.conn, self.addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(self.conn, self.addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

    def handle_client(self):
        print(f"[NEW CONNECTION] {self.addr} connected.")
        connected = True
        while connected:
            msg_length = self.conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = self.conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                print(f"[{self.addr}] {msg}")
                self.conn.send("Msg received".encode(FORMAT))

    def close(self):
        print(f"[CONNECTION CLOSED] {self.addr} closed.")
        self.conn.close()

#server = Server()
#server.handle_client()
#server.close()


class Client:
    client = None
    conn = None
    addr = None
    server = None
    port = None

    def __init__(self, server=SERVER, port=PORT):
        self.server = server
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.addr)
        '''
        print("[STARTING] server is starting...")
        self.client.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            self.conn, self.addr = self.client.accept()
            thread = threading.Thread(target=self.handle_client, args=(self.conn, self.addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")'''

    def set_address(self):
        self.addr = (self.server, self.port)

    def send(self, msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        print(self.client.recv(2048).decode(FORMAT))


#client = Client()
#client.send("Hello World!")
#client.send("Hello Everyone!")
#client.send(DISCONNECT_MESSAGE)