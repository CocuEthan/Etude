/**
 * This program get the IP address of a specified hostname with the function
 * "getaddrinfo".
 * @author Cyril Rabat
 **/
#include <sys/socket.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>

int main(int argc, char *argv[]) {
    struct addrinfo request;
    struct addrinfo *result;
    int i = 1;
    
    char IPv4_address[INET_ADDRSTRLEN];
    char IPv6_address[INET6_ADDRSTRLEN];

    // Check arguments
    if(argc != 3) {
        fprintf(stderr, "Use: %s familly address\n", argv[0]);
        fprintf(stderr, "Where:\n");
        fprintf(stderr, "\t familly: AF_INET (for IPv4) or AF_INET6 (for IPv6\n");
        fprintf(stderr, "\t address: IPv4 or IPv6 address\n");
        exit(EXIT_FAILURE);
    }

    // Initialization of hints
    memset(&request, 0, sizeof(struct addrinfo));
    request.ai_family = AF_UNSPEC; // IPv4 or IPv6
    request.ai_socktype = SOCK_STREAM;
    request.ai_flags = AI_CANONNAME;
    request.ai_protocol = 0; // any protocol
    request.ai_canonname = NULL;
    request.ai_addr = NULL;
    request.ai_next = NULL;

    // Get name
    if(getaddrinfo(argv[1], argv[2], &request, &result) == -1) {
        perror("Error getaddrinfo");
        exit(EXIT_FAILURE);
    }

    // Parse entries result
    while(result != NULL) {
        printf("Entry %d:\n", i);
        if(result->ai_family == AF_INET) {
            // IPv4 address
            if(inet_ntop(AF_INET, result->ai_addr, IPv4_address, INET_ADDRSTRLEN) == NULL)
                printf("Impossible to convert...\n");
            else
                printf("Address: %s, %s\n", result->ai_canonname, IPv4_address);
        }
        if(result->ai_family == AF_INET6) {
            // IPv6 address
            if(inet_ntop(AF_INET6, result->ai_addr, IPv6_address, INET6_ADDRSTRLEN) == NULL)
                printf("Impossible to convert...\n");
            else
                printf("Address: %s %s\n", result->ai_canonname, IPv6_address);
        }

        result = result->ai_next;
        i++;
    }
    
    return EXIT_SUCCESS;
}