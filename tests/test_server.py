import unittest

from server.server import Server


def test_server_starts_properly():
    s = Server(12345)
    assert s


def test_server_throws_if_port_already_taken():
    s1 = Server(12345)
    try:
        s2 = Server(12345)
    except OSError as e:
        assert "Only one usage of each socket address (protocol/network address/port) is normally permitted" in str(e)


test_server_starts_properly()
test_server_throws_if_port_already_taken()