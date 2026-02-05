/**
 * This program illustrates a complete client/server application using a
 * TCP socket. The server waits for a connection from a client. He create a
 * child to manage this connection. The client sends a value and the server's
 * child responds to it by multiplying that value by two.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char *argv[]) {
    int fd, n;
    struct sockaddr_in address;
    
    // Check arguments
    if(argc != 3) {
        fprintf(stderr, "Use: %s address port\n", argv[0]);
        fprintf(stderr, "Where:\n");
        fprintf(stderr, "  address: IPv4 address of the server\n");
        fprintf(stderr, "  port   : port of the server\n");
        exit(EXIT_FAILURE);
    }

    // Create socket
    if((fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }
    
    // Fill the address structure
    memset(&address, 0, sizeof(struct sockaddr_in));
    address.sin_family = AF_INET;
    address.sin_port = htons(atoi(argv[2]));
    if(inet_pton(AF_INET, argv[1], &address.sin_addr.s_addr) != 1) {
        perror("Error converting address");
        exit(EXIT_FAILURE);
    }

    // Connect to the server
    if(connect(fd, (struct sockaddr*)&address, sizeof(address)) == -1) {
        perror("Error connecting to the server");
        exit(EXIT_FAILURE);
    }

    // Send value to the server
    n = getpid();
    if(write(fd, &n, sizeof(int))== -1) {
        perror("Error sending value");
        exit(EXIT_FAILURE);
    }
    printf("Client: value sent %d\n", n);

    // Read the server response
    if(read(fd, &n, sizeof(int)) == -1) {
        perror("Error reading response");
        exit(EXIT_FAILURE);
    }
    printf("Client : valeur reçue %d.\n", n);

    // Close the socket
    if(close(fd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }

    return EXIT_SUCCESS;
}