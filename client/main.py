import socket

sentences = ['This is first test sentence']
server_address = ('localhost', 12345)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Connecting to %s port %s', server_address)
s.connect(server_address)
s.send(sentences[0].encode())
