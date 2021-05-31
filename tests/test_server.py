import os
import pickle
import socket
import sys

from common.messages import Request, RequestType

sys.path.append(os.path.join('..', 'server'))
import server

# Test constants
SERVER_PORT = 12345
BUFF_SIZE = 1024
SENTENCES = [
    'This is first test sentence',
    'This is second test sentence',
    'This is third test sentence',
    'This is fourth test sentence',
    'This is fifth test sentence'
]
SERVER_ADDRESS = ('localhost', SERVER_PORT)


def test_server_starts_properly():
    """Server starts properly."""

    # Given
    # When
    s = server.Server(SERVER_PORT)
    # Then
    assert s


def test_server_throws_if_port_already_taken():
    """Check server throws exception if specified port is already taken."""
    # Given
    # When
    s1 = server.Server(SERVER_PORT)
    try:
        s2 = server.Server(SERVER_PORT)
    except OSError as e:
        # Then
        assert "Only one usage of each socket address (protocol/network address/port) is normally permitted" in str(e)


def test_server_new_user():
    """New user connects to server."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    new_user_msg = Request(msg_type=RequestType.NEW_USER, username='jarek')
    sck.send(pickle.dumps(new_user_msg))
    srv.read_from_socket()
    response, ignored = sck.recvfrom(BUFF_SIZE)
    response_decoded = pickle.loads(response)
    # Then
    assert response_decoded.payload == 'Success'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__data) == 0


def test_server_unknown_user():
    """Users sends data to server without registering first."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    sck.send(
        pickle.dumps(Request(msg_type=RequestType.SENTENCE, username='jarek', payload=SENTENCES[0]))
    )
    srv.read_from_socket()
    response, ignored = sck.recvfrom(BUFF_SIZE)
    response_decoded = pickle.loads(response)
    # Then
    assert response_decoded.payload.startswith("Error! Address")
    assert len(srv._Server__users) == 0
    assert len(srv._Server__data) == 0


def test_user_sends_new_sentence():
    """Registered user sends new sentence."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When

    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    new_user_msg = Request(msg_type=RequestType.NEW_USER, username='jarek')
    sck.send(pickle.dumps(new_user_msg))
    srv.read_from_socket()
    response, ignored = sck.recvfrom(BUFF_SIZE)
    response_decoded = pickle.loads(response)

    sck.send(
        pickle.dumps(Request(msg_type=RequestType.SENTENCE, username='jarek', payload=SENTENCES[0]))
    )
    srv.read_from_socket()

    # Then
    assert response_decoded.payload == 'Success'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__data) == 1


def test_server_writes_successfully():
    """Check server sends data correctly"""
    # Given
    srv = server.Server(SERVER_PORT)
    # When
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    new_user_msg = Request(msg_type=RequestType.NEW_USER, username='jarek')
    sck.send(pickle.dumps(new_user_msg))
    srv.read_from_socket()
    response, ignored = sck.recvfrom(BUFF_SIZE)
    response_decoded = pickle.loads(response)
    sck.send(
        pickle.dumps(Request(msg_type=RequestType.SENTENCE, username='jarek', payload=SENTENCES[0]))
    )
    srv.read_from_socket()
    srv.write_to_socket()
    response2, ignored = sck.recvfrom(BUFF_SIZE)
    response2_decoded = pickle.loads(response2)
    # Then
    assert response_decoded.payload == 'Success'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__data) == 1
    assert SENTENCES[0] in response2_decoded.payload


def test_server_receives_data_from_multiple_users():
    """A couple of registered user send new data."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When
    sck1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck1.connect(SERVER_ADDRESS)
    new_user_msg1 = Request(msg_type=RequestType.NEW_USER, username='jarek')
    sck1.send(pickle.dumps(new_user_msg1))
    srv.read_from_socket()
    response1, ignored = sck1.recvfrom(BUFF_SIZE)
    response1_decoded = pickle.loads(response1)

    sck2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck2.connect(SERVER_ADDRESS)
    new_user_msg1 = Request(msg_type=RequestType.NEW_USER, username='tomek')
    sck2.send(pickle.dumps(new_user_msg1))
    srv.read_from_socket()
    response2, ignored = sck2.recvfrom(BUFF_SIZE)
    response2_decoded = pickle.loads(response2)

    sck3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck3.connect(SERVER_ADDRESS)
    new_user_msg1 = Request(msg_type=RequestType.NEW_USER, username='james')
    sck3.send(pickle.dumps(new_user_msg1))
    srv.read_from_socket()
    response3, ignored = sck3.recvfrom(BUFF_SIZE)
    response3_decoded = pickle.loads(response2)

    for sentence in SENTENCES:
        for user, sck in zip(['jarek', 'tomek', 'james'], [sck1, sck2, sck3]):
            msg = Request(msg_type=RequestType.SENTENCE, username=user, payload=sentence)
            sck.send(pickle.dumps(msg))
            srv.read_from_socket()

    # Then
    assert response1_decoded.payload == 'Success'
    assert response2_decoded.payload == 'Success'
    assert response3_decoded.payload == 'Success'
    assert len(srv._Server__users) == 3
    assert len(srv._Server__data) == len(SENTENCES) * 3


def test_users_delay():
    """Registered user with non zero delay sends a couple of sentences (more than N), receives only one message."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When

    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    new_user_msg = Request(msg_type=RequestType.NEW_USER, username='jarek')
    sck.send(pickle.dumps(new_user_msg))
    srv.read_from_socket()
    response, ignored = sck.recvfrom(BUFF_SIZE)
    response_decoded = pickle.loads(response)

    for snt in SENTENCES:
        msg = Request(msg_type=RequestType.SENTENCE, username='jarek', payload=snt)
        sck.send(pickle.dumps(msg))
        srv.read_from_socket()

    srv.write_to_socket()
    response2, adr = sck.recvfrom(BUFF_SIZE)
    response2_decoded = pickle.loads(response2)

    # Then
    assert response_decoded.payload == 'Success'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__data) == len(SENTENCES)
    for snt in SENTENCES:
        assert snt in response2_decoded.payload


test_server_starts_properly()
test_server_throws_if_port_already_taken()
test_server_new_user()
test_user_sends_new_sentence()
test_server_unknown_user()
test_server_writes_successfully()
test_server_receives_data_from_multiple_users()
test_users_delay()
