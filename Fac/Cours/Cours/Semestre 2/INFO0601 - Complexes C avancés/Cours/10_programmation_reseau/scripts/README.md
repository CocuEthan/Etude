# Scripts of course #10

## Compilation

To compile, type the following command:

```bash
make
```

## Programs/files

Here is the list of the generated programs or files used:
- `sockets/convert`: inet_pton and inet_ntop use
- `sockets/bindipv4`: create and name an IPv4 socket
- `sockets/bindipv6`: create and name an IPv6 socket
- `sockets/getaddrinfo`: use of *getaddrinfo* to get the IP address associated of a domain name
- `sockets/getnameinfo`: use of *getnameinfo* to get the domain name of an IP address
- `sockets/getsockname`: use of *getsockname* to get the address of a socket
- `socketUDP/`: a client/server application that uses UDP sockets
- `socketUDP_example/`: a full client/server application with UDP sockets (a time server)
- `socketTCP/`: a full client/server application with TCP sockets
- `monitoring/`: use of *pslect* to monitor descriptor files (here of pipes)
- `socketpair` : example of anonymous local sockets (*socketpair*)
- `local_socket/`: example of named local sockets