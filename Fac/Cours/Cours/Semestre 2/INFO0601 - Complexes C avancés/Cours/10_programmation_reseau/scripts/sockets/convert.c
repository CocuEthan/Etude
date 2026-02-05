/**
 * This programs shows how using inet_pton and inet_ntop to convert string to
 * IPv4 or IPv6 addresses, and vice versa.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <arpa/inet.h>

int main(int argc, char *argv[]) {
    struct in_addr IPv4_address;
    struct in6_addr IPv6_address;
    char IPv4_string[INET_ADDRSTRLEN];
    char IPv6_string[INET6_ADDRSTRLEN];
    int i;

    // Check arguments
    if(argc != 3) {
        fprintf(stderr, "Use: %s family address\n", argv[0]);
        fprintf(stderr, "Where:\n");
        fprintf(stderr, "\t family: AF_INET (for IPv4) or AF_INET6 (for IPv6\n");
        fprintf(stderr, "\t address: IPv4 or IPv6 address\n");
        exit(EXIT_FAILURE);
    }

    if(strcmp(argv[1], "AF_INET") == 0) {
        // IPv4 address

        // Convert string to network format
        if(inet_pton(AF_INET, argv[2], &IPv4_address) != 1) {
            fprintf(stderr, "Error during conversion (1)\n");
            exit(EXIT_FAILURE);
        }
        printf("Address in network format: %d\n", IPv4_address.s_addr);

        // Convert network format to string
        if(inet_ntop(AF_INET, &IPv4_address, IPv4_string, INET_ADDRSTRLEN) == NULL) {
            perror("Error during conversion (2)");
            exit(EXIT_FAILURE);
        }
        printf("Address: %s\n", IPv4_string);
    }
    else if(strcmp(argv[1], "AF_INET6") == 0) {
        // IPv6 address

        // Convert string to network format
        if(inet_pton(AF_INET6, argv[2], &IPv6_address) != 1) {
            fprintf(stderr, "Erreur lors de la conversion\n");
            exit(EXIT_FAILURE);
        }
        printf("Address in network format: ");
        for(i = 0; i < 15; i++)
            printf("%d:", (int)IPv6_address.s6_addr[i]);
        printf("%d\n", (int)IPv6_address.s6_addr[i]);

        // Convert network format to string
        if(inet_ntop(AF_INET6, &IPv6_address, IPv6_string, INET6_ADDRSTRLEN) == NULL) {
            perror("Error during conversion (3)");
            exit(EXIT_FAILURE);
        }

        printf("Address: %s\n", IPv6_string);
    }
    else {
        // Argument error
        fprintf(stderr, "Error: protocol unsupported!\n");
        exit(EXIT_FAILURE);
    }

    return EXIT_SUCCESS;
}
