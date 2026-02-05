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
    int fd, sockclient;
    struct sockaddr_un address;
    size_t size;
    char *msg;

    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s name\n", argv[0]);
        fprintf(stderr, "Où :\n");
        fprintf(stderr, "  name: the name of the local socket\n");
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

    // Name socket
    if(bind(fd, (struct sockaddr*)&address, sizeof(struct sockaddr_un)) == -1) {
        perror("Error namming socket");
        exit(EXIT_FAILURE);
    }

    // Switch the socket to passive
    if(listen(fd, 1) == -1) {
        perror("Error when switching to passive mode");
        exit(EXIT_FAILURE);
    }

    // Wait for a connection
    printf("Server: wait connection...\n");
    if((sockclient = accept(fd, NULL, NULL)) == -1) {
        perror("Error waiting connection");
        exit(EXIT_FAILURE);
    }

    // Read message: size and content
    if(read(sockclient, &size, sizeof(size_t)) == -1) {
        perror("Error reading size of the message");
        exit(EXIT_FAILURE);
    }
    if((msg = (char*)malloc(sizeof(char) * size)) == NULL) {
        perror("Error allocating");
        exit(EXIT_FAILURE);
    }
    if(read(sockclient, msg, sizeof(char) * size) == -1) {
        perror("Error reading content of the message");
        exit(EXIT_FAILURE);
    }
    printf("Server: message received '%s'.\n", msg);

    // Close sockets
    if(close(sockclient) == -1) {
        perror("Error closing communication socket");
        exit(EXIT_FAILURE);
    }
    if(close(fd) == -1) {
        perror("Error closing connection socket");
        exit(EXIT_FAILURE);
    }

    // Free memory
    free(msg);

    // Delete the entry in the system file
    if(unlink(address.sun_path) == -1) {
        fprintf(stderr, "Error deleting entry '%s'", address.sun_path);
        perror("");
        exit(EXIT_FAILURE);
    }

    printf("Server stopped.\n");

    return EXIT_SUCCESS;
}