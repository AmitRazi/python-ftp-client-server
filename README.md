# Simple FTP Server and Client

This project implements a basic File Transfer Protocol (FTP) server and client application using Python. It includes both command-line and graphical user interfaces for the client.

## Features

- Multithreaded FTP server
- Command-line and GUI client options
- Basic FTP commands: LIST, CWD, RETR, DEL, QUIT
- File upload and download functionality
- Simple and intuitive graphical user interface

## Requirements

- Python 3.6+
- tkinter (for GUI)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/simple-ftp-project.git
   cd simple-ftp-project
   ```

2. No additional installation is required if you have Python 3.6+ with tkinter.

## Usage

### Starting the Server

Run the following command to start the FTP server:

```
python main.py server
```

The server will start listening on localhost:20000 by default.

### Using the Client

#### GUI Client

To start the graphical client:

```
python main.py client
```

#### Command-line Client

The command-line client can be used directly:

```
python client.py
```

## Project Structure

- `server.py`: FTP server implementation
- `client.py`: FTP client core functionality
- `gui.py`: Graphical user interface for the client
- `main.py`: Entry point for running the server or client

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
