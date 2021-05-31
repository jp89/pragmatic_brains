class User:
    def __init__(self, username, current_index, delay=0):
        self.__username = username
        self.__current_index = current_index
        self.__delay = delay

    @property
    def username(self):
        return self.__username

    @property
    def current_index(self):
        return self.__current_index

    @current_index.setter
    def current_index(self, value):
        self.__current_index = value

    @property
    def delay(self):
        return self.__delay
