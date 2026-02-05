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
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>

#include "structures.h"

int stop = 0;

/**
 * Handler to capture the SIGINT signal.
 * @param signum the signal number
 */
void handler(int signum) {
    printf("Stop request received.\n");
    stop = 1;
}

int main(int argc, char *argv[]) {
    int sockfd;
    struct sockaddr_in server_address, client_address;
    socklen_t address_length = sizeof(struct sockaddr_in);
    request_t request;
    response_t response;
    struct sigaction action;
    struct tm *date;
    time_t hour;

    // Specify handler
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGINT, &action, NULL) == -1) {
        perror("Error positionning handler");
        exit(EXIT_FAILURE);    
    }

    // Check argumemnts
    if(argc != 2) {
        fprintf(stderr, "Use: %s port\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    // Create socket
    if((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Fill server address
    memset(&server_address, 0, sizeof(struct sockaddr_in));
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(atoi(argv[1]));
    server_address.sin_addr.s_addr = htonl(INADDR_ANY);

    // Name socket
    if(bind(sockfd, (struct sockaddr*)&server_address, sizeof(struct sockaddr_in)) == -1) {
        perror("Error naming socket");
        exit(EXIT_FAILURE);
    }

    // Wait for client requests
    while(stop == 0) {
        printf("Wait for a request (CRTL + C to stop)\n");

        // Read a request
        if(recvfrom(sockfd, &request, sizeof(request_t), 0,
                    (struct sockaddr*)&client_address, &address_length) == -1) {
            if(errno != EINTR) {
                perror("Error receiving message");
                exit(EXIT_FAILURE);
            }
        }
        else {
            // Prepare response
            hour = time(NULL);
            date = gmtime(&hour);
            response.id = request.id;
            if(request.code == CODE_HOUR)
                sprintf(response.result, "%.2dh%.2d", date->tm_hour, date->tm_min);
            else
                sprintf(response.result, "%.2d/%.2d/%4d", date->tm_mday, date->tm_mon + 1, date->tm_year + 1900);

            // Send response
            if(sendto(sockfd, &response, sizeof(response_t), 0,
                      (struct sockaddr*)&client_address, address_length) == -1) {
                perror("Error sending response");
                exit(EXIT_FAILURE);
            }
        }
    } 

    // Close socket
    if(close(sockfd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }

    printf("Server: stop.\n");

    return EXIT_SUCCESS;
}