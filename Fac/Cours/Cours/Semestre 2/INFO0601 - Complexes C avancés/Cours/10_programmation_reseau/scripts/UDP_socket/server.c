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
    struct sockaddr_in server_address, client_address;
    request_t request;
    response_t response = { "Hello to you too" };
    socklen_t size = sizeof(struct sockaddr_in);

    // Create socket
    if((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Fill server address
    memset(&server_address, 0, sizeof(struct sockaddr_in));
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(PORT);
    server_address.sin_addr.s_addr = INADDR_ANY;

    // Name socket
    if(bind(sockfd, (struct sockaddr*)&server_address, sizeof(struct sockaddr_in)) == -1) {
        perror("Error naming socket");
        exit(EXIT_FAILURE);
    }

    // Wait for a client request
    printf("Server: waiting for a request.\n");
    if(recvfrom(sockfd, &request, sizeof(request), 0, (struct sockaddr*)&client_address, &size) == -1) {
        perror("Error receiving message");
        exit(EXIT_FAILURE);
    }
    printf("Server: message received '%s'.\n", request.msg);

    // Send response
    if(sendto(sockfd, &response, sizeof(response), 0, (struct sockaddr*)&client_address, sizeof(struct sockaddr_in)) == -1) {
        perror("Error sending response");
        exit(EXIT_FAILURE);
    }
    printf("Server: response sent.\n");

    // Close socket
    if(close(sockfd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }

    printf("Server: done.\n");

    return EXIT_SUCCESS;
}