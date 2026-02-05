/**
 * The server waits for a client message and responds to it. The server
 * port is specified in "include.h".
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#include "include.h"

int main(int argc, char *argv[]) {
    int sockfd;
    struct sockaddr_in address;
    request_t request = { "Hello to you" };
    response_t response;
  
    // Create socket
    if((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Fill server address
    memset(&address, 0, sizeof(struct sockaddr_in));
    address.sin_family = AF_INET;
    address.sin_port = htons(PORT);
    if(inet_pton(AF_INET, "127.0.0.1", &address.sin_addr) != 1) {
        perror("Error converting address");
        exit(EXIT_FAILURE);
    }

    // Send request
    if(sendto(sockfd, &request, sizeof(request), 0, (struct sockaddr*)&address, sizeof(struct sockaddr_in)) == -1) {
        perror("Error sending message");
        exit(EXIT_FAILURE);
    }
    printf("Client: message sent.\n");

    // Wait for response
    if(recvfrom(sockfd, &response, sizeof(response), 0, NULL, 0) == -1) {
        perror("Error receiving response");
        exit(EXIT_FAILURE);
    }
    printf("Client: message received '%s'.\n", response.msg);

    // Close socket
    if(close(sockfd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }

    return EXIT_SUCCESS;
}
