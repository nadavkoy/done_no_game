import threading
from chat_server import *
from AES import *
import pickle

# CLIENT REQUEST IDENTIFIERS:
ENTRANCE_REQUEST_IDENTIFIER = 'ENTRANCE:'
BROADCAST_MESSAGE = 'BROADCAST:'
PRIVATE_MESSAGE = 'PRIVATE:'
RECEIVED_SONG_LIST = 'SONG_LIST??'

SONG_SEPARATOR = '##??##'

# RESPONSES TO CLIENT
SUCCESSFUL_ENTRY = 'ENTERED SUCCESSFULLY'
WRONG_DETAILS = 'WRONG DETAILS'
USER_NOT_FOUND = '** Requested user does not exist, or is not connected **'

END_OF_SONG = 'END OF SONG!'

LEAVE_PARTY = 'LEAVE PARTY'


class ClientHandler(threading.Thread):
    """ responsible for the server-client communication """

    def __init__(self, song_socket, song_address, address, socket, public_key, private_key, rsa, database):
        super(ClientHandler, self).__init__()
        self.sock = socket
        self.address = address

        self.song_socket = song_socket
        self.song_address = song_address

        # for encryption:
        self.rsa = rsa  # rsa is a Cryptonew object that we got from server as a parameter
        self.key = ''  # this variable will hold the AES that we'll get from the client
        self.public = public_key  # the public key we got from the server as a parameter
        self.private = private_key  # the private key we got from the server as a parameter
        self.aes = AESCrypt()  # creating a AESCrypt object to encrypt and decrypt with AES.

        self.database = database
        self.done_logging_in = False
        self.got_song_list = False

    def handle_user_entrance(self, entrance_details):
        """ responsible for verifying and authenticating the user's information,
            and informing the client on whether or not the entrance succeeded."""

        entrance_details = entrance_details.split(':')  # details are separated by ':'.
        entrance_type = entrance_details[1]  # entrance type: login/register.
        client_username = entrance_details[2]  # client's username entered.
        client_password = entrance_details[3]  # client's password entered.

        if entrance_type == 'register':  # if the client chose to register (connecting as a new user)

            if self.database.add_user(client_username, client_password) is False:  # if details are wrong
                self.sock.send(self.encrypt_message(WRONG_DETAILS, self.key))

            else:
                # sending an approval string and the chat history to the client.
                CONNECTED_USERS.update(
                    {client_username: [self.sock,
                                       self.key]})  # updating the connected users dictionary with client's details.
                self.sock.send(self.encrypt_message(SUCCESSFUL_ENTRY + '-' + MESSAGES, self.key))

                self.done_logging_in = True

        elif entrance_type == 'login':  # if the client chose to login (connecting as an existing user)
            if self.database.user_exists(client_username, client_password):
                # if username and password exist in the server's database

                CONNECTED_USERS.update(
                    {client_username: [self.sock,
                                       self.key]})  # updating the connected users dictionary with client's details.

                # sending an approval string and the chat history to the client.
                self.sock.send(self.encrypt_message(SUCCESSFUL_ENTRY + '-' + MESSAGES, self.key))

                self.done_logging_in = True

            else:
                # if the details the client entered don't match the database, informing the client on that.
                self.sock.send(self.encrypt_message(WRONG_DETAILS, self.key))

    def send_messages(self, message, message_type):
        """ responsible for sending the messages.
            receiving the message itself and whether it's a private or a broadcast message, sending it to the intended
            clients using their sockets which are saved in the server's 'connected users' dictionary."""

        global MESSAGES  # the chat history string, which is in the server.

        if message_type == BROADCAST_MESSAGE:
            for user_socket in CONNECTED_USERS.values():  # sending message to all the connected users.
                socket = user_socket[0]
                key = user_socket[1]
                socket.send(self.encrypt_message(message, key))

            message = message.split(':')
            sender = message[1]  # message sender
            the_message = message[2]  # message itself
            new_message = sender + ': ' + the_message  # arranging info in a presentable string
            MESSAGES += new_message + '\n'  # appending the chat history string, which will be sent to every new client.

        elif message_type == PRIVATE_MESSAGE:
            message = message.split(':')
            sender = message[1]  # message sender
            message_part = message[2].split('@')  # '@' separates the message from the requested addressee username.
            send_to = message_part[0]  # intended addressee
            the_message = message_part[1]  # message itself

            # Checking if the intended addressee is an actual user in the system, and if they are connected:
            found_user = False
            for user in CONNECTED_USERS.keys():
                if user == send_to:
                    found_user = True

            if found_user:
                # if addressee found, sending message to both the sender and the addressee
                CONNECTED_USERS[send_to][0].send(
                    self.encrypt_message(message_type + sender + ':' + the_message, CONNECTED_USERS[send_to][1]))
                CONNECTED_USERS[sender][0].send(
                    self.encrypt_message(message_type + sender + ':' + the_message, self.key))

            if found_user is False:
                # if addressee is not connected, inform the sender
                CONNECTED_USERS[sender][0].send(self.encrypt_message(USER_NOT_FOUND, self.key))

    def send_songs(self):
        """ responsible fro sending the song list to the client. """
        global SONG_LIST
        global PARTY_STARTED

        while True:
            if self.done_logging_in and SONG_LIST:

                if PARTY_STARTED is False:
                    PARTY_STARTED = True
                    start_timer()
                    print 'START TIME: ' + str(START_TIME)

                self.done_logging_in = False
                print SONG_LIST

                print ' sending songs!'

                for song in SONG_LIST:  # iterating the song list, in order to send the songs.
                    file = open(song, 'rb')  # opening file
                    song_title = song.split("\\")[-1]  # extracting song title

                    print song_title

                    #self.song_socket.send(song_title + SONG_SEPARATOR + str(time_passed()))

                    if song == SONG_LIST[0]:  # if its the first song:
                        self.song_socket.send(song_title + SONG_SEPARATOR + str(time_passed()) + SONG_SEPARATOR)

                    else:
                        self.song_socket.send(song_title + SONG_SEPARATOR + '' + SONG_SEPARATOR)

                    done_sending = False
                    while not done_sending:
                        piece = file.read(1024 * 40)  # reading 1024 bytes at a time.
                        self.song_socket.send(piece)  # sending packet.

                        if piece == '':
                            done_sending = True

                    print song_title + ' sent!'

                    file.close()  # closing file

                    self.song_socket.send(END_OF_SONG)  # sending a string that indicates the end of the file.

                    self.song_socket.recv(1024)

                    if song == SONG_LIST[-1]:  # if this is the last song in the song list, quit the loop
                        break

    def get_client_key(self):
        """ decoding the encryption key """
        self.sock.send(self.rsa.pack(self.public))  # sending the pickled public key to the client
        encrypted_key = self.sock.recv(1024)  # getting the AES key encrypted with the public key
        self.key = self.rsa.decode(encrypted_key, self.private)  # decoding the encrypted key with the private key
        self.sock.send('got the key!')

    def decrypt_message(self, encrypted_client_request):
        """ decrypts the client's request """
        return self.aes.decryptAES(self.key, encrypted_client_request)  # decrypt the message with AES key

    def encrypt_message(self, response, key):
        """ encrypts the server's response """
        return self.aes.encryptAES(key, response)  # encrypt the message with AES key

    def get_song_list(self, song_list_message):
        """ responsible for extracting the song list sent by the dj. """
        global SONG_LIST
        song_list = song_list_message.split(RECEIVED_SONG_LIST)[1]
        song_list = song_list.split(SONG_SEPARATOR)
        for song in song_list:
            SONG_LIST.append(song)

        del SONG_LIST[-1]

        print SONG_LIST

        self.got_song_list = True
        print 'got list.'

    def run(self):
        self.get_client_key()
        t = threading.Thread(target=self.send_songs, args=())
        t.start()
        while True:

            message_from_client = self.sock.recv(1024)
            message_from_client = self.decrypt_message(message_from_client)

            if message_from_client.startswith(ENTRANCE_REQUEST_IDENTIFIER):
                self.handle_user_entrance(message_from_client)

            elif message_from_client.startswith(BROADCAST_MESSAGE):
                self.send_messages(message_from_client, BROADCAST_MESSAGE)

            elif message_from_client.startswith(PRIVATE_MESSAGE):
                self.send_messages(message_from_client, PRIVATE_MESSAGE)

            elif message_from_client.startswith(RECEIVED_SONG_LIST):
                self.get_song_list(message_from_client)

            elif message_from_client.startswith(LEAVE_PARTY):
                user_left = message_from_client.split(':')[1]
                del CONNECTED_USERS[user_left]
                self.sock.close()
                self.song_socket.close()
                print 'client disconnected.'
                break
