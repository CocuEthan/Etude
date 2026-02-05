/**
 * These programs use a local socket to send a message from a client to a
 * server in the connected mode. The size is sent then the message content.
 * The name of the socket and the message are passed as argument.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char *argv[]) {
    int fd;
    struct sockaddr_un address;
    size_t size;

    // Check arguments
    if(argc != 3) {
        fprintf(stderr, "Use: %s name message\n", argv[0]);
        fprintf(stderr, "Où :\n");
        fprintf(stderr, "  name   : socket name\n");
        fprintf(stderr, "  message: message to send\n");
        exit(EXIT_FAILURE);
    }

    // Create socket
    if((fd = socket(AF_LOCAL, SOCK_STREAM, 0)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Create server address
    memset(&address, 0, sizeof(struct sockaddr_un));
    address.sun_family = AF_LOCAL;
    snprintf(address.sun_path, sizeof(struct sockaddr_un) - sizeof(sa_family_t), "%s", argv[1]);

    // Connect to the server
    if(connect(fd, (struct sockaddr*)&address, sizeof(struct sockaddr_un)) == -1) {
        perror("Error connecting to the server");
        exit(EXIT_FAILURE);
    }

    // Send message: size and content
    size = strlen(argv[2]) + 1;
    if(write(fd, &size, sizeof(size_t)) == -1) {
        perror("Error writing message size");
        exit(EXIT_FAILURE);
    }
    if(write(fd, argv[2], sizeof(char) * size) == -1) {
        perror("Error writing message content");
        exit(EXIT_FAILURE);
    }
    printf("Client: message sent.\n");

    // Close socket
    if(close(fd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }

    return EXIT_SUCCESS;
}