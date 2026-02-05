/**
 * The server sets a handler for the SIGUSR1 and SIGUSR2 signals. Then, it
 * waits for the client to send these signals.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <errno.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    pid_t pid;
    
    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s PID where PID is the PID of the 'server'\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    pid = atoi(argv[1]);
    
    // Check if the specified PID is correct
    if(kill(pid, 0) == -1) {
        if(errno == ESRCH) {
            fprintf(stderr, "The process with the PID %d doesn't exist\n", pid);
            exit(EXIT_FAILURE);
        }
        else {
            perror("Error sending the signal");
            exit(EXIT_FAILURE);
        }
    }
    printf("Process with %d is here.\n", pid);
    
    // Send the SIGUSR1 signal
    if(kill(pid, SIGUSR1) == -1) {
        perror("Error sending the SIGUSR1 signal");
        exit(EXIT_FAILURE);
    }
    printf("Signal SIGUSR1 sent.\n");
    sleep(1);
    
    // Send the SIGUSR2 signal
    if(kill(pid, SIGUSR2) == -1) {
        perror("Error sending the SIGUSR2 signal");
        exit(EXIT_FAILURE);
    }
    printf("Signal SIGUSR2 sent.\n");

    return EXIT_SUCCESS;
}