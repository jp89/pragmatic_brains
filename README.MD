# Introduction

This repository contains UDP server and client code.
Server accepts messages from 'writers' and sends them to 'readers'.
Server can handle many writers and readers that may connect at any time.

# Usage
Server, reader and writer run in infinite loop.
Please run a server first and then any number of readers and writers.
See instructions below on how to run them.

## Server
```
py run_server.py --port XYZAQ
```
Port is optional, by default server uses port 12345.

## Client reader
```
py run_reader.py --username abcdf --delay 3 --address 127.0.0.1 --port 72632 
```
Address and port are optional, by default client uses localhost:12345.
Username is mandatory.
Delay is optional, user may wish to receive packages of sentences rather than single lines.

## Client writer
```
py run_writer.py --username abcdf --address 127.0.0.1 --port 72632 
```
Address and port are optional, by default client uses localhost:12345.
Username is mandatory.
Writer blocks on reading from stdin. 
User should type text followed by new line in order to send a message.

Please see [demo](demo.mp4) for usage demonstration.

## How does it work ?

Server creates a UDP socket and accepts data from users.
Each new user send a registration request first.
Server registers user and responds with confirmation.
Registered user may start producing messages or read messages produced by other uses.

## Limitations and known problems.

### Os
Code was tested on Windows 10 10.0.19043.985.
I haven't been able to test it on Linux or MacOS.

### UDP
UDP does not guarantee that packets are received by the other side.
I decided not to implement any mechanism for retrying / ensuring they are received as this would require
substantial amount of work.

### Server architecture
Server stores all incoming messages in one list which grows as users send more data.
In real-life application that data should be stored in some sort of database, 
perhaps only the newest data should be cached in server's memory.
The same goes for storing clients metadata.

### Client architecture
Unfortunately I haven't been able to come up with a fairly simple implementation of a client 
capable of both reading and writing messages.
It is possible to read from stdin and socket without blocking with select().
However, select() does not support stdin on Windows (only sockets).
I considered running separate thread for getting user's input but this would make the code much more
complicated. Even if getting data from both stdin and network socket was implemented there's another problem to solve:
printing prompt and messages received from server in the same console window requires using non-standard
platform specific libraries.


Please contact me in case of any questions: jarek.p89@gmail.com