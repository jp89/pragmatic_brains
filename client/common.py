import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='UDP Server. Connected users may send sentences to each other.')
    parser.add_argument('--address', type=str, default='localhost',
                        help='UDP server IP address.')
    parser.add_argument('--port', type=int, default=12345,
                        help='UDP server port. ')
    parser.add_argument('--username', required=True, type=str, help='Every sentence sent to the server from this'
                                                                    'process will be prepended with username.')
    parser.add_argument('--delay', type=int, default=0, help='Receive sentences from server in packages of at least N'
                                                             ' sentences. Default value - zero - means server will send'
                                                             ' sentences without any delay.')
    return parser.parse_args()


def display_banner():
    banner = """
      __  _____  ___        ___          __ 
     / / / / _ \/ _ \  ____/ (_)__ ___  / /_
    / /_/ / // / ___/ / __/ / / -_) _ \/ __/
    \____/____/_/     \__/_/_/\__/_//_/\__/ 

    """
    print(banner)


def register_user(sck, username, delay, address, port):
    try:
        sck.sendto('NewUser:{},N:{}'.format(username, delay).encode(), (address, port))
        response, ignored = sck.recvfrom(1024)
        if response.decode() != 'Success':
            raise RuntimeError('Failed to register user, reason: {}'.format(response.decode()))
    except ConnectionError as e:
        raise RuntimeError('Server unavailable. Make sure it is running.')




