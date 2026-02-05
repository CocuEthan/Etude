/**
 * This program positions a handler for the SIGINT signal and waits for
 * this signal.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

/**
 * Handler for SIGUSR1 and SIGUSR2 signals.
 * @param signum the received signal number
 */
void handler(int signum) {
    printf("Signal received\n");
}

int main() {
    struct sigaction action;
    
    // Specify the SIGINT signal
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGINT, &action, NULL) == -1) {
        perror("Error positioning handler");
        exit(EXIT_FAILURE);
    }
    
    // Wait for the SIGINT signal
    printf("Press CRTL+C\n");
    pause();
    printf("I'm in the main function\n");
    
    return EXIT_SUCCESS;
}