import pickle

import client_common
import socket

from common.messages import Request, RequestType


def run(address, port, username, delay):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sck:
        try:
            client_common.register_user(sck, username, delay, address, port)
        except Exception as e:
            print('Client failed to connect. Reason: {}', str(e))
            exit(1)

        print("Running UDP client - sender!")
        while True:
            sentence = input("What would you like to say? ")
            msg = Request(msg_type=RequestType.SENTENCE, username=username, payload=sentence)
            try:
                sck.sendto(pickle.dumps(msg), (address, port))
            except ConnectionError as e:
                print('Server unavailable.')


def main(cmd_args):
    client_common.display_banner()
    run(cmd_args.address, cmd_args.port, cmd_args.username, cmd_args.delay)


if __name__ == "__main__":
    args = client_common.parse_args()
    main(args)
