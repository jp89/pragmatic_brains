from server import Server


def main():
    server = Server(12345)
    server.run()


if __name__ == "__main__":
    main()