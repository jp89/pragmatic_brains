import pickle
import socket
import server.user
import common
from common.messages import RequestType


class Server:
    BUF_SIZE = 1024
    USERNAME_LENGTH = 5

    def __init__(self, port):
        # Create a IPv4 datagram socket, see https://docs.python.org/3/library/socket.html
        self.__port = port
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__server_socket.setblocking(False)
        self.__server_socket.bind(('localhost', port))  # reachable by any address this machine has
        # Maps address to user metadata (user name, output delay)
        self.__users = {}
        # Output queue
        self.__data = []

    def run(self):
        print('Starting UDP server on port ' + str(self.__port), flush=True)
        while True:
            self.read_from_socket()
            self.write_to_socket()

    def read_from_socket(self):
        try:
            msg, address = self.__server_socket.recvfrom(Server.BUF_SIZE)
            if address in self.__users:
                self.handle_existing_user(address, msg)
            else:
                self.handle_new_user(address, msg)
            # else:
            #     self.handle_unknown_user(address)
        except (BlockingIOError, ConnectionResetError) as e:
            # These errors occur on Windows, not sure about Linux.
            # BlockingIOError - nothing to read
            # ConnectionResetError - last sendto failed due to client shutting down socket on his side,
            # we don't care about that in connectionless protocol
            pass

    def handle_new_user(self, address, msg):
        new_message = pickle.loads(msg)
        if new_message.type == RequestType.NEW_USER:
            self.__users[address] = server.user.User(username=new_message.username, delay=int(new_message.delay),
                                                     messages_sent=0)
            response = common.messages.Response('Success')
            self.__server_socket.sendto(pickle.dumps(response), address)
        else:
            response = common.messages.Response('Error! Address {} is not registered as user.'.format(address))
            self.__server_socket.sendto(pickle.dumps(response), address)

    def handle_existing_user(self, address, msg):
        new_msg = pickle.loads(msg)
        self.__data.append(self.__users[address].username + ': ' + new_msg.payload)

    def write_to_socket(self):
        try:
            for address, usr in self.__users.items():
                delta = len(self.__data) - usr.messages_sent
                if delta >= usr.delay:
                    response = common.messages.Response('\n'.join(self.__data[delta * (-1):]))
                    self.__server_socket.sendto(pickle.dumps(response), address)
                    usr.messages_sent = usr.messages_sent + delta
        except Exception as e:
            print(e)
