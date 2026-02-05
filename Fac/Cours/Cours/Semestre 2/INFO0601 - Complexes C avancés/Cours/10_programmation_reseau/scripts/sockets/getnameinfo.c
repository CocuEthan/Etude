/**
 * This program display the domain name associated to an IP address.
 * @author Cyril Rabat
 **/
#include <sys/socket.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>

#define MAX_SIZE 1024

int main(int argc, char *argv[]) {
    struct sockaddr_in address;
    char hostname[NI_MAXHOST], servicename[NI_MAXSERV];

    // Check arguments
    if(argc != 3) {
        fprintf(stderr, "Use: %s address port\n", argv[0]);
        fprintf(stderr, "\tWhere:\n");
        fprintf(stderr, "\t\t- address: IPv4 address\n");
        fprintf(stderr, "\t\t- port   : port\n");        
        exit(EXIT_FAILURE);
    }

    // Fill address structure
    memset(&address, 0, sizeof(struct sockaddr_in));
    address.sin_family = AF_INET;
    inet_pton(AF_INET, argv[1], &address.sin_addr.s_addr);
    address.sin_port = htons(atoi(argv[2]));

    // Get the domain name
    if(getnameinfo((struct sockaddr*)&address, sizeof(struct sockaddr_in),
                   hostname, sizeof(hostname), servicename, sizeof(servicename), 
                   NI_NAMEREQD) == -1) {
        perror("Error getting domain name");
        exit(EXIT_FAILURE);
    }

    printf("Host: %s, Service: %s\n", hostname, servicename);

    return(EXIT_SUCCESS);
}