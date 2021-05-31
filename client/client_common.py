import argparse
import pickle

from common.messages import Request, RequestType


def parse_args():
    parser = argparse.ArgumentParser(description='Udp server client.')
    parser.add_argument('--address', type=str, default='localhost',
                        help='UDP server IP address.')
    parser.add_argument('--port', type=int, default=12345,
                        help='UDP server port. ')
    parser.add_argument('--username', required=True, type=str, help='Every sentence sent to the server from this'
                                                                    'process will be prepended with username.')
    parser.add_argument('--delay', type=int, default=1, help='Receive sentences from server in packages of at least N'
                                                             ' sentences. Default value - one - means server will send'
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
        msg = Request(msg_type=RequestType.NEW_USER, username=username, delay=delay)
        sck.sendto(pickle.dumps(msg), (address, port))
        response, ignored = sck.recvfrom(1024)
        response_decoded = pickle.loads(response)
        if response_decoded.payload != 'Success':
            raise RuntimeError('Failed to register user, reason: {}'.format(response.decode()))
    except ConnectionError as e:
        raise RuntimeError('Server unavailable. Make sure it is running.')




