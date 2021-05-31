from enum import Enum


class RequestType(Enum):
    """Helper class, defines types of requests sent by clients to the server"""

    NEW_USER = 1,
    SENTENCE = 2


class Request:
    """Helper class, defines format of messages sent from client to the server."""

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
    """Helper class, defines format of messages sent from server to clients."""

    def __init__(self, payload):
        self.__payload = payload

    @property
    def payload(self):
        return self.__payload
