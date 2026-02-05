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
  
    // Check arguments
    if(argc != 3) {
        fprintf(stderr, "Use: %s name message\n", argv[0]);
        fprintf(stderr, "Où :\n");
        fprintf(stderr, "  name   : socket name\n");
        fprintf(stderr, "  message: message to send\n");
        exit(EXIT_FAILURE);
    }

    // Create socket
    if((sockfd = socket(AF_LOCAL, SOCK_DGRAM, 0)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Create server address
    memset(&address, 0, sizeof(struct sockaddr_un));
    address.sun_family = AF_LOCAL;
    snprintf(address.sun_path, sizeof(struct sockaddr_un) - sizeof(sa_family_t), "%s", argv[1]);

    // Send message: size and content
    size = strlen(argv[2]) + 1;
    if(sendto(sockfd, &size, sizeof(size_t), 0, (struct sockaddr*)&address, sizeof(struct sockaddr_un)) == -1) {
        perror("Error sending message size");
        exit(EXIT_FAILURE);
    }
    if(sendto(sockfd, argv[2], sizeof(char) * size, 0, (struct sockaddr*)&address, sizeof(struct sockaddr_un)) == -1) {
        perror("Error sending message content");
        exit(EXIT_FAILURE);
    } 
    printf("Client: message sent.\n");

    // Close socket
    if(close(sockfd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }

    return EXIT_SUCCESS;
}
