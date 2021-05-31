import os
import socket
import unittest
import sys
sys.path.append(os.path.join('..', 'server'))
import server

# Test constants
SERVER_PORT = 12345
BUFF_SIZE = 1024
NEW_USER_MSGS = [
    'NewUser:tomek,N:0',
    'NewUser:jarek,N:5',
    'NewUser:james,N:7'
    ]
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
    sck.send(NEW_USER_MSGS[0].encode())
    srv.read_from_socket()
    response = sck.recvfrom(BUFF_SIZE)
    # Then
    assert response[0].decode() == 'Success'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__output_buffer) == 0
    assert srv._Server__current_index == 0


def test_server_unknown_user():
    """Users sends data to server without registering first."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    sck.send(SENTENCES[1].encode())
    srv.read_from_socket()
    response = sck.recvfrom(BUFF_SIZE)
    # Then
    assert response[0].decode().startswith("Error! Address")
    assert len(srv._Server__users) == 0
    assert len(srv._Server__output_buffer) == 0
    assert srv._Server__current_index == 0


def test_user_sends_new_sentence():
    """Registered user sends new sentence."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When

    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    sck.send(NEW_USER_MSGS[0].encode())
    srv.read_from_socket()
    response = sck.recvfrom(BUFF_SIZE)

    sck.send(SENTENCES[1].encode())
    srv.read_from_socket()

    # Then
    assert response[0].decode() == 'Success'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__output_buffer) == 1
    assert srv._Server__current_index == 1


def test_one_user_sends_multiple_sentences():
    """Registered user sends multiple sentences, check if output buffer grows accordingly"""
    # Given
    srv = server.Server(SERVER_PORT)
    # When
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    sck.send(SENTENCES[0].encode())
    srv.read_from_socket()
    response = sck.recvfrom(BUFF_SIZE)

    sck.send(SENTENCES[1].encode())
    srv.read_from_socket()

    # Then
    assert response[0].decode() == 'Ack'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__output_buffer) == 1
    assert srv._Server__current_index == 1


def test_server_writes_successfully():
    """Registered user sends multiple sentences, check if output buffer grows accordingly"""
    # Given
    srv = server.Server(SERVER_PORT)
    # When
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    sck.send(NEW_USER_MSGS[0].encode())
    srv.read_from_socket()
    response = sck.recvfrom(BUFF_SIZE)

    sck.send(SENTENCES[1].encode())
    srv.read_from_socket()
    srv.write_to_socket()
    response2 = sck.recvfrom(BUFF_SIZE)

    # Then
    assert response[0].decode() == 'Success'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__output_buffer) == 1
    assert srv._Server__current_index == 1
    assert SENTENCES[1] in response2[0].decode()


def test_server_receives_data_from_multiple_users():
    """A couple of registered user send new data."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When

    sck1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck1.connect(SERVER_ADDRESS)
    sck1.send(NEW_USER_MSGS[0].encode())
    srv.read_from_socket()
    response1 = sck1.recvfrom(BUFF_SIZE)

    sck2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck2.connect(SERVER_ADDRESS)
    sck2.send(NEW_USER_MSGS[1].encode())
    srv.read_from_socket()
    response2 = sck2.recvfrom(BUFF_SIZE)

    sck3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck3.connect(SERVER_ADDRESS)
    sck3.send(NEW_USER_MSGS[2].encode())
    srv.read_from_socket()
    response3 = sck3.recvfrom(BUFF_SIZE)

    for sentence in SENTENCES:
        sck1.send(sentence.encode())
        srv.read_from_socket()
        sck2.send(sentence.encode())
        srv.read_from_socket()
        sck3.send(sentence.encode())
        srv.read_from_socket()

    # Then
    assert response1[0].decode() == 'Success'
    assert response2[0].decode() == 'Success'
    assert response3[0].decode() == 'Success'
    assert len(srv._Server__users) == 3
    assert len(srv._Server__output_buffer) == len(SENTENCES) * 3
    assert srv._Server__current_index == len(SENTENCES) * 3


def test_users_delay():
    """Registered user with non zero delay sends a couple of sentences (more than N), receives only one message."""
    # Given
    srv = server.Server(SERVER_PORT)
    # When

    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.connect(SERVER_ADDRESS)
    sck.send(NEW_USER_MSGS[0].encode())
    srv.read_from_socket()
    response = sck.recvfrom(BUFF_SIZE)

    for snt in SENTENCES:
        sck.send(snt.encode())
        srv.read_from_socket()
    srv.write_to_socket()
    reponse2, adr = sck.recvfrom(BUFF_SIZE)

    # Then
    assert response[0].decode() == 'Success'
    assert len(srv._Server__users) == 1
    assert len(srv._Server__output_buffer) == len(SENTENCES)
    decoded_response = reponse2.decode()
    for snt in SENTENCES:
        assert snt in decoded_response


# test_server_starts_properly()
# test_server_throws_if_port_already_taken()
# test_server_new_user()
# test_user_sends_new_sentence()
# test_server_unknown_user()
# test_server_writes_successfully()
# test_server_receives_data_from_multiple_users()
test_users_delay()