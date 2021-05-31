from enum import Enum


class RequestType(Enum):
    NEW_USER = 1,
    SENTENCE = 2


class Request:
    def __init__(self, msg_type, username, delay=1, payload=None):
        self.__type = msg_type
        self.__username = username
        self.__delay = delay
        self.__payload = payload

    @property
    def type(self):
        return self.__type

    @property
    def username(self):
        return self.__username

    @property
    def delay(self):
        return self.__delay

    @property
    def payload(self):
        return self.__payload


class Response:
    def __init__(self, payload):
        self.__payload = payload

    @property
    def payload(self):
        return self.__payload
