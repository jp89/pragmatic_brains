class User:
    """Represents user that connected to the server, stores user's defined delay and number of messages sent so far."""

    def __init__(self, username, messages_sent, delay=0):
        self.__username = username
        self.__messages_sent = messages_sent
        self.__delay = delay

    @property
    def username(self):
        return self.__username

    @property
    def messages_sent(self):
        return self.__messages_sent

    @messages_sent.setter
    def messages_sent(self, value):
        self.__messages_sent = value

    @property
    def delay(self):
        return self.__delay
