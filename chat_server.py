import socket
import chat_client_handler
from KeyGenerator import *
from silent_disco_database import *
from song_server import *
import time

CONNECTED_USERS = {}  # will contain the connected users information ({username: socket})
MESSAGES = ''  # will contain the chatting history, for the new users to receive.
SONG_LIST = []

START_TIME = 0.0
PARTY_STARTED = False


class Server(object):
    def __init__(self, port):
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', port))
        self.server_socket.listen(10)

        # for encryption:
        self.rsa = Cryptonew()  # creating a new Cryptonew object to encrypt and decrypt with RSA
        self.public_key = self.rsa.get_public()  # getting the public RSA key
        self.private_key = self.rsa.get_private()  # getting the private RSA key

    def accept(self):
        return self.server_socket.accept()


def start_timer():
    """ responsible for measuring the time since the beginning of the party """
    global PARTY_STARTED
    global START_TIME
    START_TIME = time.time()


def time_passed():
    return time.time() - START_TIME


def main():
    # creating the server and the song server.
    server = Server(60000)
    song_server = Server(60100)

    chat_socket, chat_address = server.accept()  # accepting the dj socket (only one accept!)
    client_hand = chat_client_handler.ClientHandler(None, None, chat_address, chat_socket,
                                                    server.public_key, server.private_key, server.rsa, Database())
    client_hand.start()

    while True:
        chat_socket, chat_address = server.accept()
        song_socket, song_address = song_server.accept()

        # creating client handler
        client_hand = chat_client_handler.ClientHandler(song_socket, song_address, chat_address, chat_socket,
                                                        server.public_key, server.private_key, server.rsa, Database())
        client_hand.start()


if __name__ == '__main__':
    main()
