import pickle
import socket
import server.user
import common
from common.messages import RequestType


class Server:
    """Chat-like server acting as a middle men between writers and subscribers."""

    """
    See readme.md for implementation details, limitations and design choices.
    """

    BUF_SIZE = 1024  # max size of a single packet sent over udp socket

    def __init__(self, port):
        # Create IPv4, datagram socket, see https://docs.python.org/3/library/socket.html
        self.__port = port
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__server_socket.setblocking(False)  # don't block on read of write
        self.__server_socket.bind(('localhost', port))  # reachable by any address this machine has
        # Users 'database'.
        # Keys - address tuples (ip, port)
        # Values - User objects
        # User object keep track of the defined delay and messages already sent.
        self.__users = {}
        # Messages sent by users are stored here
        self.__data = []

    def run(self):
        """Server runs in an infinite loop, listening for the new data and sending data if applicable."""

        print('Starting UDP server on port ' + str(self.__port), flush=True)
        while True:
            self.maybe_read_from_socket()
            self.maybe_write_to_socket()

    def maybe_read_from_socket(self):
        """Reads data from udp socket, immediately returns if there's no data to be processed."""

        """
        Server expects packets not bigger than maximum Server.BUF_SIZE bytes.
        When running on Windows BlockingIOError is thrown if there's no data to be read.
        ConnectionError may be thrown if last sendto() called on the server socket failed (e.g. due to the other side
        closing their socket) - it's safe to ignore in this particular case. UDP is connectionless protocol,
        this project doesn't handle disconnected users (or monitoring "connection" in general).   
        """

        try:
            msg, address = self.__server_socket.recvfrom(Server.BUF_SIZE)
            if address in self.__users:
                self.handle_existing_user(address, msg)
            else:
                self.handle_new_user(address, msg)
            # else:
            #     self.handle_unknown_user(address)
        except (BlockingIOError, ConnectionError) as e:
            # These errors occur on Windows, not sure about Linux.
            # BlockingIOError - nothing to read
            # ConnectionResetError - last sendto failed
            pass

    def handle_new_user(self, address, msg):
        """Adds user to internal in-memory "database". Sends confirmation if successful, error message otherwise. """

        """
        When connecting to the server for the first time user is expected to send "hi" message in order to register.
        This is handled by client/client_common.py module.
        If - for whatever reason - server receives data from not registered user other than registration request it will
        send error message in response.
        """

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
        """Add sentence sent by already registered user to messages "database". """

        """
        Messages from all users are stored in one, common list.
        """

        new_msg = pickle.loads(msg)
        self.__data.append(self.__users[address].username + ': ' + new_msg.payload)

    def maybe_write_to_socket(self):
        """Iterates over users "database", sends messages to the registered users."""

        """
        For each user check if there are new messages that could be sent, consider delay defined by users that
        prefer not to receive each new message but rather packets of several messages.
        
        Each User object keeps track of how many messages have already been sent.
        That value is compared if the number of total messages present in the 'database'.
        New message is sent only if the difference between these values is greater or equal to the defined delay.
        """

        try:
            for address, usr in self.__users.items():
                delta = len(self.__data) - usr.messages_sent
                if delta >= usr.delay:
                    response = common.messages.Response('\n'.join(self.__data[delta * (-1):]))
                    self.__server_socket.sendto(pickle.dumps(response), address)
                    usr.messages_sent = usr.messages_sent + delta
        except Exception as e:
            print(e)
