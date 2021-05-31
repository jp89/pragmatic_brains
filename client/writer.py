import common
import socket


def run(address, port, username, delay):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sck:
        try:
            common.register_user(sck, username, delay, address, port)
        except Exception as e:
            print('Client failed to connect. Reason: {}', str(e))
            exit(1)

        print("Running UDP client - sender!")
        while True:
            sentence = input("What would you like to say? ")
            try:
                sck.sendto(sentence.encode(), (address, port))
            except ConnectionError as e:
                print('Server unavailable.')


def main(cmd_args):
    common.display_banner()
    run(cmd_args.address, cmd_args.port, cmd_args.username, cmd_args.delay)


if __name__ == "__main__":
    args = common.parse_args()
    main(args)
