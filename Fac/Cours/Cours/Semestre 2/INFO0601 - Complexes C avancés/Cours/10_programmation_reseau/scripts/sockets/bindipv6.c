/**
 * This programs uses the socket function to create an Internet socket (IPv6)
 * and the bind function to name it.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

int main(int argc, char *argv[]) {
    int sockfd;
    struct sockaddr_in6 address;

    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s port\n", argv[0]);
        fprintf(stderr, "Where:\n");
        fprintf(stderr, "  port: server port\n");
        exit(EXIT_FAILURE);
    }

    // Create socket (not connected)
    if((sockfd = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }
    printf("The socket was successfully created.\n");

    // Create server address
    memset(&address, 0, sizeof(struct sockaddr_in6));
    address.sin6_family = AF_INET6;
    address.sin6_addr = in6addr_any;
    address.sin6_port = htons(atoi(argv[1]));

    // Name socket
    if(bind(sockfd, (struct sockaddr*)&address, sizeof(struct sockaddr_in6)) == -1) {
        perror("Error naming socket");
        exit(EXIT_FAILURE);
    }
    printf("The socket was successfully named.\n");

    // Close socket
    if(close(sockfd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }
    printf("The socket was successfully closed.\n");
  
    return EXIT_SUCCESS;
}