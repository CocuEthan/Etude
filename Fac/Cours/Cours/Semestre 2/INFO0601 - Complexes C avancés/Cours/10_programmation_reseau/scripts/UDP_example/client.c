/**
 * This program illustrates a complete client/server application using a
 * UDP socket. The server waits for a connection from a client. He create a
 * child to manage this connection. The client sends a value and the server's
 * child responds to it by multiplying that value by two.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>

#include "structures.h"

int alarme = 0;

void handler(int signum) {
    alarme++;
}

int main(int argc, char *argv[]) {
    int sockfd;
    struct sockaddr_in address;
    request_t request;
    response_t response;
    struct sigaction action;
    int stop = 0;

    // Check arguments
    if((argc != 4) || ((strcmp(argv[3], "HOUR") != 0) &&
       (strcmp(argv[3], "DATE") != 0))) {
        fprintf(stderr, "Use: %s address port mode\n", argv[0]);
        fprintf(stderr, "Ou :\n");
        fprintf(stderr, "  address: IPv4 server address\n");
        fprintf(stderr, "  port   : server port\n");
        fprintf(stderr, "  mode   : HOUR for the hour and DATE for the date\n");
        exit(EXIT_FAILURE);
    }

    // Position handler
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGALRM, &action, NULL) == -1) {
        perror("Error positionning handler");
        exit(EXIT_FAILURE);    
    }

    // Create socket
    if((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Fill the address structure
    memset(&address, 0, sizeof(struct sockaddr_in));
    address.sin_family = AF_INET;
    address.sin_port = htons(atoi(argv[2]));
    if(inet_pton(AF_INET, argv[1], &address.sin_addr) != 1) {
        perror("Error converting address");
        exit(EXIT_FAILURE);
    }

    // Send request
    request.id = getpid();
    if(strcmp(argv[3], "HOUR") == 0)
        request.code = CODE_HOUR;
    else
        request.code = CODE_DATE;

    while(stop == 0) {
        // Send request
        if(sendto(sockfd, &request, sizeof(request_t), 0, 
                  (struct sockaddr*)&address, sizeof(struct sockaddr_in)) == -1) {
            perror("Error sending request");
            exit(EXIT_FAILURE);
        }
        printf("Client: request sent.\n");

        // Receive response
        alarm(1);
        if(recvfrom(sockfd, &response, sizeof(response_t), 0, NULL, 0) == -1) {
            if(errno == EINTR) {
                if(alarme == 3) {
                    printf("The server is not responding...\n");
                    exit(EXIT_FAILURE);
                }
                else
                    printf("The server is not responding, new try.\n");
            }
            else {
                perror("Error receiving response");
                exit(EXIT_FAILURE);
            }
        }
        else {
            alarm(0);
            printf("Client: response received = (%d) : %s\n", response.id, response.result);
            stop = 1;
        }
    }

    // Close socket
    if(close(sockfd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }

    return EXIT_SUCCESS;
}