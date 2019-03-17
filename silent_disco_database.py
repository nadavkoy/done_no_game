import sqlite3


class Database(object):
    """ the Silent Disco database. """
    def __init__(self):
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.users_cursor = self.conn.cursor()

        self.users_cursor.execute(
            """ CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT) """)

    def add_user(self, username, password):
        """ given a username and a password, adds them to the Users database if not taken. """
        if not self.username_password_taken(username, password):
            self.users_cursor.execute("INSERT INTO users VALUES(?, ?)", (username, password))
            self.conn.commit()
            return True  # user added successfully.

        return False  # username was taken. Therefore, user couldn't be added.

    def username_password_taken(self, username, password):
        """ returns 'true' if username is already taken, 'false' otherwise. """
        self.users_cursor.execute('select * from users')
        for user in self.users_cursor:  # iterating the Users table
            if user[0] == username or user[1] == password:  # check if the wanted username already exists
                return True
        return False

    def user_exists(self, username, password):
        """ checks if the username and password entered actually belong to an existing user. """
        self.users_cursor.execute('select * from users')
        for user in self.users_cursor:  # iterating the Users table
            if user[0] == username and user[1] == password:  # check if the details match any of the the existing ones.
                return True
        return False  # there is no such user with such password. therefore, return False.



