import os
import socket
import logging
from threading import Thread


class FTPServer:
    """A simple multithreaded FTP server."""

    def __init__(self, host='localhost', port=20000, buffer_size=1024):
        """Initialize the FTP server with host, port, and buffer size."""
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind_and_listen()

    def bind_and_listen(self):
        """Bind the server socket and start listening for incoming connections."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            logging.info(f"FTP server listening on port {self.port}")
        except socket.error as e:
            logging.error(f"Failed to bind and listen on {self.host}:{self.port}. Error: {e}")
            raise

    def start(self):
        """Start accepting client connections."""
        logging.info("FTP server is running...")
        try:
            while True:
                client_socket, client_addr = self.server_socket.accept()
                logging.info(f"Connection established with {client_addr}")
                client_handler = Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket):
        """Handle communication with a connected client."""
        try:
            client_socket.sendall(b"Welcome to our FTP server!\n")
            while True:
                data = client_socket.recv(self.buffer_size)
                if not data:
                    break

                command, arg = self.parse_command(data.decode())
                if not command:
                    client_socket.sendall(b"Invalid command\n")
                    continue

                response = self.handle_command(client_socket, command, arg)
                if not response:
                    client_socket.sendall(b"Error: Command failed or syntax error\n")
        except ConnectionResetError:
            logging.warning("Client connection reset.")
        finally:
            client_socket.close()

    def parse_command(self, data):
        """Parse the client's command and argument."""
        parts = data.strip().split(maxsplit=1)
        cmd = parts[0].upper() if parts else None
        arg = parts[1] if len(parts) > 1 else None
        return cmd, arg

    def handle_command(self, client_socket, command, arg):
        """Execute the client's command."""
        command_handlers = {
            'LIST': self.handle_list_cmd,
            'CWD': self.handle_cwd_cmd,
            'HELP': self.handle_help_cmd,
            'RETR': self.handle_retr_cmd,
            'DEL': self.handle_dele_cmd,
            'QUIT': self.handle_quit_cmd
        }

        handler = command_handlers.get(command)
        if handler:
            return handler(client_socket, arg)
        else:
            return False

    def handle_list_cmd(self, client_socket, arg):
        """Handle the LIST command to list directory contents."""
        if arg:
            return False
        try:
            files = os.listdir('.')
            dirs = [f"+{d}" for d in files if os.path.isdir(d)]
            files_only = [f"-{f}" for f in files if os.path.isfile(f)]
            sorted_files = sorted(dirs) + sorted(files_only)
            file_list = '\n'.join(sorted_files) + '\n'
            client_socket.sendall(file_list.encode())
            return True
        except OSError as e:
            logging.error(f"Error listing files: {e}")
            return False

    def handle_cwd_cmd(self, client_socket, arg):
        """Handle the CWD command to change the working directory."""
        if not arg:
            return False
        try:
            os.chdir(arg)
            current_dir_name = os.path.basename(os.getcwd())
            message = f"Directory changed to {current_dir_name}\n"
            client_socket.sendall(message.encode())
            return True
        except OSError as e:
            logging.error(f"Error changing directory to {arg}: {e}")
            return False

    def handle_help_cmd(self, client_socket, arg=None):
        """Handle the HELP command to display available commands."""
        help_message = (
            "The following commands are available:\n"
            "LIST - List the contents of the current directory\n"
            "CWD <directory> - Change the current working directory\n"
            "RETR <file> - Retrieve a file from the server\n"
            "DEL <file> - Remove a file\n"
            "QUIT - Disconnect from the server\n"
            "HELP - Display this help message\n"
        )
        client_socket.sendall(help_message.encode())
        return True

    def handle_retr_cmd(self, client_socket, file_name):
        """Handle the RETR command to send a file to the client."""
        if not file_name:
            return False
        try:
            with open(file_name, 'rb') as file:
                file_size = os.stat(file_name).st_size
                client_socket.sendall(f"{file_size}\n".encode())
                while True:
                    chunk = file.read(self.buffer_size)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
            return True
        except OSError as e:
            logging.error(f"Error retrieving file {file_name}: {e}")
            return False

    def handle_dele_cmd(self, client_socket, file_name):
        """Handle the DEL command to delete a file."""
        if not file_name:
            return False
        try:
            os.remove(file_name)
            client_socket.sendall(f"Successfully deleted file {file_name}\n".encode())
            return True
        except OSError as e:
            logging.error(f"Error deleting file {file_name}: {e}")
            return False

    def handle_quit_cmd(self, client_socket, arg=None):
        """Handle the QUIT command to close the client connection."""
        client_socket.sendall(b"Closing connection. Goodbye!\n")
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = FTPServer()
    server.start()
