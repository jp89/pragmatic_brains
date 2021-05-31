import pickle

import client_common
import socket


def run(address, port, username, delay):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sck:
        try:
            client_common.register_user(sck, username, delay, address, port)
        except Exception as e:
            print('Client failed to connect. Reason: {}', str(e))
            exit(1)

        print("Running UDP client - subscriber!")
        while True:
            try:
                msg, ignored = sck.recvfrom(1024)
                msg_decoded = pickle.loads(msg)
                print(msg_decoded.payload)
            except ConnectionError as e:
                print('Server unavailable.')


def main(cmd_args):
    client_common.display_banner()
    run(cmd_args.address, cmd_args.port, cmd_args.username, cmd_args.delay)


if __name__ == "__main__":
    args = client_common.parse_args()
    main(args)
