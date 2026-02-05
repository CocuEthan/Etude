/**
 * These programs use a local socket to send a message from a client to a
 * server in the not connected mode. The size is sent then the message content.
 * The name of the socket and the message are passed as argument.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    int sockfd;
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
    if((sockfd = socket(AF_LOCAL, SOCK_DGRAM, 0)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Create address server
    memset(&address, 0, sizeof(struct sockaddr_un));
    address.sun_family = AF_LOCAL;
    snprintf(address.sun_path, sizeof(struct sockaddr_un) - sizeof(sa_family_t), "%s", argv[1]);

    // Name socket
    if(bind(sockfd, (struct sockaddr*)&address, sizeof(struct sockaddr_un)) == -1) {
        perror("Error naming socket");
        exit(EXIT_FAILURE);
    }

    // Read message from client
    printf("Serve waits for a message.\n");
    if(recvfrom(sockfd, &size, sizeof(size_t), 0, NULL, NULL) == -1) {
        perror("Error reading message size");
        exit(EXIT_FAILURE);
    }
    if((msg = (char*)malloc(sizeof(char) * size)) == NULL) {
        perror("Error allocating");
        exit(EXIT_FAILURE);
    }
    if(recvfrom(sockfd, msg, sizeof(char) * size, 0, NULL, NULL) == -1) {
        perror("Error reading message content");
        exit(EXIT_FAILURE);
    }
    printf("Server: message received '%s'.\n", msg);

    // Closing socket
    if(close(sockfd) == -1) {
        perror("Error closing socket");
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