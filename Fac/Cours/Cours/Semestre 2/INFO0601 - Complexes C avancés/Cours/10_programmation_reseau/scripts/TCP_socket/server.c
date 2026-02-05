/**
 * This program illustrates a complete client/server application using a
 * TCP socket. The server waits for a connection from a client. He create a
 * child to manage this connection. The client sends a value and the server's
 * child responds to it by multiplying that value by two.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <errno.h>
#include <sys/wait.h>

int stop = 0;

/**
 * Handler to capture the SIGINT and the SIGCHLD signals.
 * @param signum the signal number
 */
void handler(int signum) {
    int r;

    if(signum == SIGINT) {
        printf("Stop request received.\n");
        stop = 1;
    }
    
    // Wait for children end
    do {
        r = waitpid(-1, NULL, WNOHANG);
    } while((r != -1) || (errno == EINTR));
}

int main(int argc, char *argv[]) {
    int fd, sockclient, n;
    struct sockaddr_in address;
    struct sigaction action;

    // Specify handler
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGCHLD, &action, NULL) == -1) {
        perror("Error positioning handler (1)");
        exit(EXIT_FAILURE);    
    }
    if(sigaction(SIGINT, &action, NULL) == -1) {
        perror("Error positioning handler (2)");
        exit(EXIT_FAILURE);    
    }

    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s port\n", argv[0]);
        fprintf(stderr, "Where:\n");
        fprintf(stderr, "  port: the server port\n");
        exit(EXIT_FAILURE);
    }

    // Create socket
    if((fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Fill server address
    memset(&address, 0, sizeof(struct sockaddr_in));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons(atoi(argv[1]));

    // Name socket
    if(bind(fd, (struct sockaddr*)&address, sizeof(struct sockaddr_in)) == -1) {
        perror("Error naming socket");
        exit(EXIT_FAILURE);
    }

    // Switch the socket in passive mode
    if(listen(fd, 1) == -1) {
        perror("Error switching socket in passive mode");
        exit(EXIT_FAILURE);
    }

    while(stop == 0) {
        // Wait for a connexion
        printf("Server: waiting for a connexion...\n");
        if((sockclient = accept(fd, NULL, NULL)) == -1) {
            if(errno != EINTR) {
                perror("Error waiting connexion");
                exit(EXIT_FAILURE);
            }
        }
        else {
            if((n = fork()) == -1) {
                perror("Error creating child");
                exit(EXIT_FAILURE);
            }
        
            if(n == 0) {
                // Close socket
                if(close(fd) == -1) {
                    perror("Error closing socket (1)");
                    exit(EXIT_FAILURE);
                }
                
                // Read value
                if(read(sockclient, &n, sizeof(int)) == -1) {
                    perror("Error reading value");
                    exit(EXIT_FAILURE);
                }
                printf("Server-child: value received '%d'.\n", n);
                
                // Send response
                n *= 2;
                if(write(sockclient, &n, sizeof(int)) == -1) {
                    perror("Error sending value");
                    exit(EXIT_FAILURE);
                }
                printf("Server-child: value sent '%d'.\n", n);

                // Close socket
                if(close(sockclient) == -1) {
                    perror("Error closing socket (2)");
                    exit(EXIT_FAILURE);
                }
                
                printf("Server-child: done.\n");
                
                exit(EXIT_SUCCESS);
            }
            else {
                // Close socket
                if(close(sockclient) == -1) {
                    perror("Error closing socket");
                    exit(EXIT_FAILURE);
                }
            }
        }
    }
    
    // Close socket
    if(close(fd) == -1) {
        perror("Error closing socket");
        exit(EXIT_FAILURE);
    }

    printf("Server done.\n");

    return EXIT_SUCCESS;
}