import re
import socket
import user


def parse_new_user_registration_message(txt):
    pattern = '(^NewUser:)([a-zA-Z0-9]{5})(,N:)([0-9]{1,2})$'
    if match := re.search(pattern, txt):
        username = match.group(2)
        delay = match.group(4)
        return username, delay
    else:
        raise ValueError('Expected new user registration message, got something else instead: {}'.format(txt))


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
        # Output queue.
        # TODO: Once server receives more than self.__output_max_size sentences it starts overriding
        # output buffer so it doesn't grow infinitely.
        self.__output_buffer = []
        self.__current_index = 0
        # self.__output_max_size = 1024

    def run(self):
        print('Starting UDP server on port ' + str(self.__port))
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
            # ConnectionResetError - last server_socket sendto failed due to client shutting down socket on his side
            pass

    def handle_new_user(self, address, msg):
        msg_decoded = msg.decode()
        try:
            username, delay = parse_new_user_registration_message(msg_decoded)
            self.__users[address] = user.User(username=username, delay=int(delay), current_index=self.__current_index)
            self.__server_socket.sendto('Success'.encode(), address)
        except ValueError as e:
            self.__server_socket.sendto('Error! Address {} is not registered as user.'.format(address).encode(), address)

    def handle_existing_user(self, address, msg):
        self.__output_buffer.append(self.__users[address].username + ': ' + msg.decode())
        self.__current_index = self.__current_index + 1

    def write_to_socket(self):
        try:
            for address, usr in self.__users.items():
                if self.__current_index - usr.current_index > usr.delay:
                    self.__server_socket.sendto('\n'.join(self.__output_buffer[usr.current_index:]).encode(), address)
                    usr.current_index = self.__current_index
        except Exception as e:
            print(e)
