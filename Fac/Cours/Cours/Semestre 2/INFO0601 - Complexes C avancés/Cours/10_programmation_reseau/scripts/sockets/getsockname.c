/**
 * This program creates a IPv4 socket and names it with a random port.
 * It uses "getsockname" to get this port.
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
    struct sockaddr_in address, address2;
    unsigned short port;
    char IPv4[INET_ADDRSTRLEN];

    // Create socket
    if((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }
    printf("Socket successfully created.\n");

    // Fill server address
    memset(&address, 0, sizeof(struct sockaddr_in));
    address.sin_family = AF_INET;
    address.sin_port = 0; // Random port
    address.sin_addr.s_addr = INADDR_ANY;

    // Name socket
    if(bind(sockfd, (struct sockaddr*)&address, sizeof(struct sockaddr_in)) == -1) {
        perror("Error naming socket");
        exit(EXIT_FAILURE);
    }
    printf("Socket successfully named.\n");
    
    socklen_t size = sizeof(struct sockaddr_in);
    if(getsockname(sockfd, (struct sockaddr*)&address2, &size) == -1) {
        perror("Error getting socket name");
        exit(EXIT_FAILURE);
    }
    
    // Convert address
    port = ntohs(address2.sin_port);
    if(inet_ntop(AF_INET, &address2.sin_addr, IPv4, INET_ADDRSTRLEN) == NULL) {
        perror("Error converting address");
        exit(EXIT_FAILURE);
    }
    printf("Address is %s and port is %d\n", IPv4, port);

    // Close socket
    if(close(sockfd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }
  
    return EXIT_SUCCESS;
}