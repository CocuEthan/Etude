/**
* The server waits to receive the SIGUSR1 signal sent by the client.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

int main(int argc, char *argv[]) {
    pid_t pid;
    
    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s PID where PID is the PID of the 'server'\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    pid = atoi(argv[1]);
    
    // Send the SIGUSR1 signal
    if(kill(pid, SIGUSR1) == -1) {
        perror("Error sending signal");
        exit(EXIT_FAILURE);
    }
    printf("Signal SIGUSR1 sent.\n");
  
    return EXIT_SUCCESS;
}