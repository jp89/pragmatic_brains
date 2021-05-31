import argparse
import server


def display_banner():
    banner = """
      __  _____  ___
     / / / / _ \/ _ \  ___ ___ _____  _____ ____
    / /_/ / // / ___/ (_-</ -_) __/ |/ / -_) __/
    \____/____/_/    /___/\__/_/  |___/\__/_/
    
    """
    print(banner)


def main(args):
    display_banner()
    s = server.Server(args.port)
    s.run()


def parse_args():
    parser = argparse.ArgumentParser(description='UDP Server. Connected users may send sentences to each other.')
    parser.add_argument('--port', type=int, default=12345,
                        help='Port used by UDP server. Clients should connect to that port.')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)