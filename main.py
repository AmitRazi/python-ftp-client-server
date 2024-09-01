import argparse
from server import FTPServer
from gui import WelcomeScreen


def main():
    parser = argparse.ArgumentParser(description='Run FTP server or client.')
    parser.add_argument('mode', choices=['server', 'client'], help='Mode to run: server or client.')

    args = parser.parse_args()

    if args.mode == 'server':
        server = FTPServer()
        server.start()
    elif args.mode == 'client':
        root = WelcomeScreen()
        root.mainloop()


if __name__ == "__main__":
    main()
