import socket
import sys
import select
import logging


class FTPClient:
    """A simple FTP client to interact with an FTP server."""

    def __init__(self, host='127.0.0.1', port=20000, buffer_size=1024):
        """Initialize the FTP client with server details and buffer size."""
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.ftp_socket = None
        self.connect_to_server()

    def connect_to_server(self):
        """Establish a connection to the FTP server."""
        try:
            self.ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ftp_socket.connect((self.host, self.port))
            self._recv_welcome_message()
        except (socket.error, socket.timeout) as e:
            logging.error(f"Failed to connect to {self.host}:{self.port}. Error: {e}")
            sys.exit(1)

    def _recv_welcome_message(self):
        """Receive and display the welcome message from the server."""
        try:
            data = self.ftp_socket.recv(self.buffer_size)
            logging.info(data.decode().strip())
        except socket.error as e:
            logging.error(f"Failed to receive welcome message. Error: {e}")

    def send_command(self, command):
        """Send a command to the FTP server."""
        try:
            self.ftp_socket.sendall(command.encode())
        except socket.error as e:
            logging.error(f"Failed to send command: {command}. Error: {e}")
            return None
        return self._receive_response()

    def _receive_response(self):
        """Receive a response from the FTP server."""
        try:
            data = self.ftp_socket.recv(self.buffer_size)
            return data.decode().strip()
        except socket.error as e:
            logging.error(f"Failed to receive response from server. Error: {e}")
            return None

    def list_files(self):
        """Handle the LIST command to retrieve and return a list of files."""
        response = self.send_command("LIST")
        if response:
            return response.splitlines()
        return []

    def change_directory(self, directory):
        """Handle the CWD command to change the working directory."""
        return self.send_command(f"CWD {directory}")

    def retrieve_file(self, filename):
        """Handle the RETR command to download a file from the server."""
        command = f"RETR {filename}"
        self.send_command(command)

        with open(filename, 'wb') as file:
            file_size = self._receive_file_size()
            if file_size is None:
                logging.error("Failed to retrieve file size.")
                return

            self._download_file(file, file_size, filename)

    def _receive_file_size(self):
        """Receive the file size from the server."""
        file_size_str = b''
        while True:
            data = self.ftp_socket.recv(1)
            file_size_str += data
            if b'\n' in data:
                break
        try:
            return int(file_size_str.strip())
        except ValueError:
            logging.error("Received invalid file size.")
            return None

    def _download_file(self, file, file_size, filename):
        """Download a file from the server."""
        received_bytes = 0
        paused = False
        while received_bytes < file_size:
            if select.select([sys.stdin], [], [], 0)[0]:
                paused = self._handle_pause(paused)

            if paused:
                continue

            data = self.ftp_socket.recv(self.buffer_size)
            received_bytes += len(data)
            file.write(data)
            logging.info(f"Received {received_bytes} of {file_size} bytes for file {filename}")

    def _handle_pause(self, paused):
        """Handle pausing and resuming the download."""
        input_data = sys.stdin.readline().strip()
        if input_data == '':
            if paused:
                logging.info("Resuming download.")
                return False
            else:
                logging.info("Download paused. Press Enter to resume.")
                return True
        return paused

    def delete_file(self, filename):
        """Handle the DELE command to delete a file on the server."""
        return self.send_command(f"DELE {filename}")

    def quit(self):
        """Handle the QUIT command to close the connection and exit."""
        response = self.send_command("QUIT")
        if response:
            logging.info(response)
        self.close_connection()

    def close_connection(self):
        """Close the socket connection to the FTP server."""
        if self.ftp_socket:
            self.ftp_socket.close()
            logging.info("Connection closed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = FTPClient()
